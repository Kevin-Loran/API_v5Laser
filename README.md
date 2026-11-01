# API V5 Laser

**API de processamento e vetorização de imagens para preparação de arquivos destinados ao corte a laser.**

Projeto desenvolvido no contexto de uma atividade de extensão universitária, com foco na aplicação de tecnologias de inteligência artificial e automação em processos de micro e pequenas empresas.

A solução foi desenvolvida para a V5 Laser, empresa do segmento de corte a laser, com o objetivo de explorar a automatização de etapas do tratamento e da vetorização de imagens utilizadas no processo produtivo.

> **Status:** Protótipo experimental em desenvolvimento.

---

## Sobre o projeto

No fluxo de trabalho de empresas que utilizam corte a laser, imagens recebidas de clientes podem apresentar baixa resolução, ruídos, compressão ou outros problemas que dificultam sua preparação para utilização em softwares de desenho e edição vetorial.

Parte desse processo exige intervenção manual para tratar imagens, ajustar contornos e convertê-las em formatos vetoriais.

A API V5 Laser foi desenvolvida para automatizar parte dessa preparação, utilizando processamento de imagens e vetorização para gerar diferentes alternativas de arquivos SVG a partir de uma única imagem enviada.

A proposta é reduzir o trabalho manual inicial e facilitar a etapa posterior de revisão e ajuste no software de edição vetorial, como o CorelDRAW.

## Objetivos

* Automatizar parte do processo de preparação de imagens.
* Gerar alternativas de vetorização a partir de uma imagem original.
* Explorar diferentes estratégias de processamento de imagens.
* Reduzir intervenções manuais nas etapas iniciais do fluxo de trabalho.
* Facilitar a integração entre processamento automatizado e ferramentas de edição vetorial.

## Tecnologias utilizadas

| Tecnologia | Aplicação                                         |
| ---------- | ------------------------------------------------- |
| Python     | Linguagem principal do projeto                    |
| FastAPI    | Desenvolvimento da API REST                       |
| Pillow     | Leitura, normalização e processamento de imagens  |
| VTracer    | Conversão de imagens rasterizadas em arquivos SVG |
| Uvicorn    | Servidor ASGI para execução da aplicação          |
| Zipfile    | Compactação dos arquivos SVG                      |
| Tempfile   | Gerenciamento de arquivos temporários             |

## Arquitetura e funcionamento

O funcionamento da aplicação segue um fluxo de processamento:

1. O usuário envia uma imagem por meio de uma requisição HTTP.
2. A API recebe e valida o arquivo.
3. A imagem é normalizada utilizando Pillow.
4. O processamento gera três alternativas de vetorização.
5. O VTracer converte as imagens processadas em arquivos SVG.
6. Os resultados são agrupados em um arquivo ZIP.
7. A API disponibiliza o arquivo compactado para download.

### Alternativas de vetorização

A aplicação gera três versões diferentes para permitir a comparação dos resultados.

| Arquivo                    | Estratégia                     | Descrição                                                                         |
| -------------------------- | ------------------------------ | --------------------------------------------------------------------------------- |
| `01_binary_direto.svg`     | Vetorização binária direta     | Envia a imagem original normalizada ao VTracer utilizando o modo binário.         |
| `02_color_direto.svg`      | Vetorização colorida           | Realiza a vetorização preservando informações de cores.                           |
| `03_binary_controlado.svg` | Vetorização binária controlada | Aplica escala de cinza, suavização gaussiana e limiarização antes da vetorização. |

Na terceira alternativa, são utilizados:

* Gaussian Blur: raio de 0.45.
* Threshold: 160.
* Conversão para imagem binária antes da vetorização.

Essas estratégias permitem observar como diferentes abordagens de processamento influenciam o resultado vetorial.

## Estrutura do projeto

```text
API_V5_Laser/
│
├── main.py
│
├── requirements.txt
│
└── README.md
```

## Instalação e execução

### 1. Pré-requisitos

* Python instalado.
* Git (opcional, para clonar o repositório).
* Ambiente virtual Python.

### 2. Clone o repositório

```bash
git clone https://github.com/Kevin-Loran/API_v5Laser.git
```

Entre na pasta:

```bash
cd API_v5Laser
```

### 3. Crie um ambiente virtual

```bash
python -m venv .venv
```

### 4. Ative o ambiente virtual

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Instale as dependências

```bash
pip install -r requirements.txt
```

### 6. Execute a aplicação

```bash
python -m uvicorn main:app --reload
```

A API estará disponível em:

```text
http://127.0.0.1:8000
```

## Endpoints disponíveis

A aplicação disponibiliza dois endpoints principais.

### GET /

Verifica se a API está em execução.

**Resposta:**

```json
{
    "message": "API V5 Laser em execução.",
    "endpoint": "POST /vectorize-test",
    "documentation": "/docs",
    "status": "experimental"
}
```

### POST /vectorize-test

Recebe uma imagem e realiza o processamento para gerar três alternativas de vetorização.

**Entrada:**

* Arquivo de imagem enviado por `multipart/form-data`.
* Campo esperado: `file`.

**Saída:**

Arquivo ZIP contendo:

```text
testes_vetorizacao.zip
│
├── 01_binary_direto.svg
├── 02_color_direto.svg
└── 03_binary_controlado.svg
```

### Documentação interativa

A API utiliza a documentação automática do FastAPI.

Após iniciar o servidor, acesse:

```text
http://127.0.0.1:8000/docs
```

Nessa interface é possível visualizar os endpoints, enviar imagens e testar as requisições.

## Tratamento de arquivos

A aplicação implementa alguns mecanismos para controlar a entrada de dados:

* Validação do formato da imagem.
* Limite de tamanho de arquivo de 15 MB.
* Limite de resolução de 25 megapixels.
* Tratamento de imagens com transparência, utilizando fundo branco.
* Tratamento de erros durante a leitura e o processamento.
* Utilização de diretórios temporários para armazenar arquivos intermediários.

Os arquivos temporários são removidos ao término do processamento. A aplicação não implementa armazenamento permanente das imagens recebidas ou dos SVGs gerados.

## Limitações conhecidas

A vetorização automatizada não garante que o arquivo SVG resultante esteja pronto para fabricação.

Durante os testes e análises do projeto, foram identificadas limitações que exigem atenção:

* Formação de contornos duplicados.
* Espessamento de linhas.
* Perda de detalhes pequenos.
* Ruídos provenientes de imagens comprimidas.
* Deformação de elementos em imagens de baixa resolução.
* Necessidade de revisão manual dos resultados.

Por esse motivo, os arquivos gerados devem passar por inspeção e ajustes em ferramentas de edição vetorial antes de serem utilizados no processo produtivo.

A aplicação não substitui o CorelDRAW nem realiza, nesta versão, uma validação geométrica completa dos arquivos para corte a laser.

## Próximos passos

Entre as possibilidades de evolução do projeto estão:

* Aprimoramento dos algoritmos de pré-processamento.
* Comparação sistemática da qualidade das três alternativas.
* Implementação de critérios de validação dos arquivos SVG.
* Identificação de contornos duplicados e caminhos abertos.
* Detecção de linhas e elementos que possam comprometer o corte.
* Desenvolvimento de uma interface para facilitar a utilização da API.
* Avaliação dos resultados com arquivos reais do fluxo de trabalho da empresa.

## Contexto acadêmico

Este projeto integra a atividade de extensão universitária **IA para Micro e Pequenas Empresas**, desenvolvida em parceria com a V5 Laser.

A iniciativa busca explorar aplicações práticas de inteligência artificial, processamento de imagens e automação para identificar oportunidades de melhoria em processos empresariais.

---

**Desenvolvimento:** Kevin Loran de Oliveira Manoel e Sofia Ramos de Morais.

**Instituição:** Universidade São Judas Tadeu.

**Empresa parceira:** V5 Laser.
