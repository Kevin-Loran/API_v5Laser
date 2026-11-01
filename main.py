import io
import logging
import tempfile
import zipfile

from pathlib import Path

import vtracer

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from PIL import (
    Image,
    ImageFilter,
    ImageOps,
    UnidentifiedImageError
)

app = FastAPI(
    title="API V5 Laser",
    description="API experimental para vetorização de imagens.",
    version="2.0.0"
)

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 15 * 1024 * 1024

MAX_IMAGE_PIXELS = 25_000_000

ALLOWED_FORMATS = {
    "PNG",
    "JPEG",
    "WEBP",
    "BMP",
    "TIFF"
}

@app.get("/")
def home():

    return {
        "message": "API V5 Laser em execução.",
        "endpoint": "POST /vectorize-test",
        "documentation": "/docs",
        "status": "experimental"
    }

def load_and_normalize_image(file_bytes: bytes):

    try:

        image = Image.open(io.BytesIO(file_bytes))

        image_format = image.format

        if image_format and image_format.upper() not in ALLOWED_FORMATS:

            raise HTTPException(
                status_code=415,
                detail="Formato de imagem não suportado."
            )

        width, height = image.size

        if width * height > MAX_IMAGE_PIXELS:

            raise HTTPException(
                status_code=413,
                detail="Imagem com resolução muito alta."
            )

        image = ImageOps.exif_transpose(image)

        image.load()

    except HTTPException:

        raise

    except (
        UnidentifiedImageError,
        OSError,
        ValueError
    ) as error:

        raise HTTPException(
            status_code=400,
            detail="O arquivo enviado não é uma imagem válida."
        ) from error

    if image.mode in ("RGBA", "LA") or (
        image.mode == "P" and "transparency" in image.info
    ):

        rgba_image = image.convert("RGBA")

        background = Image.new(
            "RGBA",
            rgba_image.size,
            (255, 255, 255, 255)
        )

        image = Image.alpha_composite(
            background,
            rgba_image
        ).convert("RGB")

    else:

        image = image.convert("RGB")

    return image


def trace_to_svg(
    input_path,
    output_path,
    colormode,
    color_precision=6,
    layer_difference=16
):

    vtracer.convert_image_to_svg_py(

        str(input_path),

        str(output_path),

        colormode=colormode,

        hierarchical="stacked",

        mode="spline",

        filter_speckle=4,

        color_precision=color_precision,

        layer_difference=layer_difference,

        corner_threshold=60,

        length_threshold=4.0,

        max_iterations=10,

        splice_threshold=45,

        path_precision=3
    )

    if not output_path.exists() or output_path.stat().st_size == 0:

        raise RuntimeError(
            "O VTracer não conseguiu gerar o arquivo SVG."
        )

def create_vectorization_variants(original_image, workdir):

    original_path = workdir / "entrada_original.png"

    controlled_path = workdir / "entrada_controlada.png"

    # Salva a imagem original normalizada.

    original_image.save(
        original_path,
        format="PNG"
    )

    binary_svg = workdir / "01_binary_direto.svg"

    trace_to_svg(

        input_path=original_path,

        output_path=binary_svg,

        colormode="binary"

    )

    color_svg = workdir / "02_color_direto.svg"

    trace_to_svg(

        input_path=original_path,

        output_path=color_svg,

        colormode="color",

        color_precision=6,

        layer_difference=16

    )

    grayscale = ImageOps.grayscale(original_image)

    # Suavização leve para reduzir ruídos pontuais.

    softened = grayscale.filter(
        ImageFilter.GaussianBlur(radius=0.45)
    )

    # Conversão para preto e branco usando limiar 160.

    controlled = softened.point(

        lambda pixel: 255 if pixel >= 160 else 0

    )

    controlled.convert("RGB").save(

        controlled_path,

        format="PNG"

    )

    controlled_svg = workdir / "03_binary_controlado.svg"

    trace_to_svg(

        input_path=controlled_path,

        output_path=controlled_svg,

        colormode="binary"

    )

    return [

        binary_svg,

        color_svg,

        controlled_svg

    ]

@app.post("/vectorize-test")
async def vectorize_test(file: UploadFile = File(...)):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Nome do arquivo não informado."
        )

    try:

        content = await file.read(MAX_FILE_SIZE + 1)

        if not content:

            raise HTTPException(
                status_code=400,
                detail="O arquivo enviado está vazio."
            )

        if len(content) > MAX_FILE_SIZE:

            raise HTTPException(
                status_code=413,
                detail="O arquivo excede o limite de 15 MB."
            )


        image = load_and_normalize_image(content)


        with tempfile.TemporaryDirectory() as temp_dir:

            workdir = Path(temp_dir)

            # Gera as três alternativas.

            svg_files = create_vectorization_variants(

                image,

                workdir

            )

            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(

                zip_buffer,

                mode="w",

                compression=zipfile.ZIP_DEFLATED

            ) as archive:

                for svg_file in svg_files:

                    archive.write(

                        svg_file,

                        arcname=svg_file.name

                    )

            zip_buffer.seek(0)

        return StreamingResponse(

            zip_buffer,

            media_type="application/zip",

            headers={

                "Content-Disposition":
                'attachment; filename="testes_vetorizacao.zip"'

            }

        )

    except HTTPException:

        raise

    except Exception as error:

        logger.exception(
            "Erro durante o processo de vetorização."
        )

        raise HTTPException(

            status_code=500,

            detail="Erro interno durante a vetorização."

        ) from error

    finally:

        await file.close()