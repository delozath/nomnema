# Research Library Project

## 1. Arquitectura de folders
<details>
<summary> research-library (click para mostrar) </summary>
<pre><code>
  research-library/
  ├── bibliography/
  │   └── master.bib
  │
  ├── documents/
  │   ├── Garcia2024EdgeSeg/
  │   │   ├── Garcia2024EdgeSeg.pdf
  │   │   ├── Garcia2024EdgeSeg-supplement.pdf
  │   │   └── Garcia2024EdgeSeg-notes.md
  │   │
  │   ├── Garcia2024FedECG/
  │   │   ├── Garcia2024FedECG.pdf
  │   │   └── Garcia2024FedECG-code.url
  │   │
  │   └── Lopez2025TinyUS/
  │       └── Lopez2025TinyUS.pdf
  │
  ├── projects/
  └── scripts/
</pre></code>
</details>

La innovación es contar con un folder por artículo relevante

Archivos complementarios (`-supplement.pdf`, `-notes.md`, `-code.url`) se agregan manualmente; fuera del alcance del script.


## Historias de usuario

### Organizar PDF [init]

```
FEATURE: Initialize App [SUCCESS]
  AS [user]
  PERFORM setup predifined output

  SCENARIO: entry is going to be stored into master.bib
  WHEN master.bib is valid
  AND master.bib is correctly loaded

  SCENARIO: entry is going to be stored into clipboard
  WHEN master.bib is not valid or null
  THEN warning message: "Entry is copied to clipboard because the entry is not valid or null"

  SCENARIO: app error is going to be displayed
  GIVEN save into master.bib file flag == true
  AND master.bib file is not valid or null
  THEN raise Error "Save into biblatex file flag is true, then copy entry to clipboard is not available"
```

### Organizar PDF [Execute]

**Success**
```
FEATURE: Agregar referencia [SUCCESS]
  AS [user]
  PERFORM retrieve bib entry
  THEN Añadir entrada a master.bib
  AND mover el PDF al folder correspondiente
  GIVEN PDF válido

  SCENARIO: success execution saved into master.bib: all inputs
    GIVEN [input: PDF] del artículo válido
    AND [input: DOI] del mismo artículo válido
    AND [input: path | master.bib] valido
    WHEN script sea ejecutado
    AND mostrar [output: mensaje] 
        "entrada agregada y archivo agregado a biblioteca"
  
  SCENARIO: success execution saved into master.bib: retrieve DOI from PDF
    GIVEN [input: PDF] del artículo válido
    AND [input: path | master.bib] valido
    WHEN script sea ejecutado
    AND retrieve from DOI from PDF success
    THEN mostrar [output: mensaje] 
         "entrada agregada y archivo agregado a biblioteca"

  SCENARIO: success execution copied to clipboard: all inputs
    GIVEN [input: PDF] del artículo válido
    AND [input: DOI] del mismo artículo válido
    AND [input: path | master.bib] no valido o ausente
    WHEN script sea ejecutado
    AND mostrar [output: mensaje] 
        "archivo master.bib no localizado, entrada copiada a portapapeles"
  
  SCENARIO: success execution copied to clipboard: retrieve DOI from PDF
    GIVEN [input: PDF] del artículo válido
    AND [input: path | master.bib] no valido o ausente
    WHEN script sea ejecutado
    AND retrieve from DOI from PDF success
    THEN mostrar [output: mensaje] 
         "archivo master.bib no localizado, entrada copiada a portapapeles"

  SCENARIO: idempotent re-run
    GIVEN [input: PDF] del artículo válido
    AND PDF ya reubicado y entrada ya existente en master.bib para el mismo DOI
    WHEN script sea ejecutado
    THEN mostrar [output: mensaje] 
         "entrada y archivo ya existentes, no se reprocesa"

  SCENARIO: MOD duplicado detectado
    GIVEN [input: MOD] provisto por config/Hydra
    AND MOD ya usado por otro AuthorYear en master.bib/documents
    WHEN script sea ejecutado
    THEN mostrar [output: ventana selección] con MODs disponibles
    AND usuario selecciona MOD final

  SCENARIO: revisión de abstract
    GIVEN entrada bib recuperada
    WHEN abstract extraído del PDF (o vacío si no se pudo extraer)
    THEN mostrar [output: ventana edición] con abstract sanitizado
    AND usuario confirma, edita o pega abstract manualmente
    AND sanitizar abstract final antes de persistir
```

**Error**

```
FEATURE: Agregar referencia [ERROR]
  AS [user]
  PERFORM retrieve bib entry
  THEN Añadir entrada a master.bib
  AND mover el PDF al folder correspondiente

  SCENARIO: error execution saved into master.bib: all inputs
    GIVEN [input: PDF] del artículo no válido
    OR [input: DOI] del mismo artículo no válido
    ANY [input: path | master.bib] valido o no
    WHEN script sea ejecutado
    AND raise [output: mensaje] 
        "error al intentar agregar entrada a biblioteca"
  
  SCENARIO: error execution saved into master.bib: error retrieve DOI from PDF
    GIVEN [input: PDF] del artículo válido
    ANY [input: path | master.bib] valido o no
    WHEN script sea ejecutado
    AND error retrieve from DOI from PDF
    THEN mostrar [output: mensaje] 
         "error al intentar obtener la entrada biblatex"
  
  SCENARIO: error move PDF
   GIVEN [input: PDF] del artículo válido
   AND [input: path | master.bib] valido
   WHEN move PDF to folder but cannot
   AND raise Error
        "error al intentar mover el PDF"

  SCENARIO: error duplicate entry en master.bib
   GIVEN [input: PDF] del artículo válido
   AND entrada recuperada (DOI) ya existe en master.bib
   AND no es una re-ejecución idéntica (PDF aún no reubicado)
   WHEN script sea ejecutado
   AND raise Error
        "error: la entrada ya existe en master.bib"

```


#### S1.0: Overview
- Inputs
  - PDF file
  - doi
  - MOD (config/Hydra override; si hay duplicidad, selección interactiva)
- Outputs
  - append to master.bib file
  - clipboard

------
## Arquitectura

### 1. ports
- [ ] Error def — tipos de error de dominio (validación, red, storage, duplicado) que propagan las demás capas
- [ ] Service Interface — contrato común de los servicios que orquestan un flujo (DOI given, DOI from PDF, etc.)
- [ ] Validator Interface (`Validator[T]`) — contrato genérico para validar un valor (DOI, path) sin red
- [ ] Loader Interface — contrato para cargar un archivo (PDF, master.bib) desde disco
- [ ] Extractor Interface — contrato para extraer un dato (DOI) del contenido de un PDF
- [ ] Retriever Interface — contrato para obtener la entrada bibliográfica dado un DOI u otra fuente, con red
- [ ] Sanitize Interface — contrato para limpiar/normalizar texto (DOI, abstract) antes de usarlo o mostrarlo
- [ ] Key Generator Interface — contrato para construir el slug `AuthorYearMOD` y resolver colisiones
- [ ] Storage Interface — contrato para persistir la entrada (master.bib o clipboard)
- [ ] Relocator Interface — contrato para mover/renombrar el PDF a su carpeta final
- [ ] Config Interface — ya implementado vía Hydra/.env (`PDFFileManager`); expone MOD y demás paths
- [ ] Abstract Extractor Interface — contrato para extraer el abstract del contenido del PDF
- [ ] Interactive Selector Interface (ventana selección MOD) — contrato para presentar una lista de opciones y devolver la selección del usuario
- [ ] Abstract Editor Interface (ventana edición abstract) — contrato para mostrar un texto editable y devolver el texto final del usuario

### 2. domain
- [ ] Pipeline registry — resuelve qué servicios/adapters concretos usa el Orchestrator en cada corrida
- [x] Sanitize text — lógica pura de limpieza/normalización de texto, sin dependencias externas
- [ ] Key/slug builder — lógica pura para construir y normalizar `AuthorYearMOD`
- [ ] Error handling — manejo y propagación centralizada de los errores de dominio
- [ ] Logging básico — registra eventos y errores a stdout/archivo (uso personal, sin auditoría formal)
- [ ] Gestión de biblatex file
  - [x] Loader
  - [ ] Saver
- [x] Mover archivos PDF
- [x] Loader PDF — implementa `Loader Interface`; lee el PDF desde disco

### 3. adapters
- [x] Extract DOI from PDF — implementa `Extractor Interface`; usa markitdown, requiere texto extraíble (PDF escaneado sin texto falla); busca DOI solo en los primeros 2000 caracteres extraídos
- [x] Retrieve Biblatex Entry (DOI) — implementa `Retriever Interface`; consulta una API externa (ej. Crossref) por DOI y devuelve la entrada bib; maneja la dependencia de red internamente
- [x] Retrieve Biblatex Entry (fuentes alternativas: sitio del artículo, PubMed, PMC) — implementa `Retriever Interface`; intercambiable con el anterior vía API retriever
- [x] Validate DOI format — implementa `Validator Interface`; valida el formato del DOI sin red
- [ ] Validate master.bib path — implementa `Validator Interface`; valida que la ruta exista y sea escribible
- [ ] Extract Abstract from PDF — implementa `Abstract Extractor Interface`; markitdown/Ollama Qwen u similar, best-effort (falla en PDFs a doble columna)
- [ ] MOD Selector Window — implementa `Interactive Selector Interface`; lista MODs existentes en caso de duplicidad
- [ ] Abstract Editor Window — implementa `Abstract Editor Interface`; usa `Sanitize Interface` antes de mostrar y sobre el texto pegado manualmente

### 4. services
- [ ] DOI given Service -> hereda de Service Interface; valida y resuelve a entrada bib un DOI ya provisto por el usuario
  - [x] Check DOI (usa `Validator Interface`, sin red)
  - [x] Retrieve DOI (usa `Retriever Interface`, con red)

- [ ] DOI from PDF Service -> hereda de DOI given Service; obtiene el DOI a partir del PDF cuando no se provee directamente
  - [x] Extract DOI (usa `Extractor Interface`)
  - [x] Si succeed:
    - [x] Check DOI
    - [x] Retrieve DOI
  - [x] otro:
    - [x] raise error

- [ ] MOD Resolution Service -> usa `Interactive Selector Interface`; determina el MOD final, con selección interactiva si hay colisión
  - [ ] Toma MOD de Config Interface (CLI/Hydra)
  - [ ] Check duplicidad contra `master.bib` y `documents/`
  - [ ] Sin duplicidad: usa el MOD tal cual
  - [ ] Con duplicidad: invoca MOD Selector Window con la lista de MODs disponibles

- [ ] Abstract Review Service -> usa `Abstract Extractor Interface` + `Abstract Editor Interface` + `Sanitize Interface`; obtiene el abstract final revisado por el usuario
  - [ ] Extrae abstract del PDF (best-effort)
  - [ ] Sanitiza antes de mostrar
  - [ ] Muestra en Abstract Editor Window: usuario confirma, edita o pega manualmente
  - [ ] Si pegado manual: sanitiza de nuevo
  - [ ] Inyecta abstract final en el campo `abstract` de la entrada bib

- [ ] Key Generation Service -> usa `Key Generator Interface` + `Sanitize Interface`; produce el slug único que identifica al artículo
  - [ ] Construye `AuthorYearMOD` siempre a partir de la entrada bib ya recuperada (nunca de input crudo) y del MOD ya resuelto
  - [ ] Resuelve colisiones de slug (mismo AuthorYearMOD, distinto DOI) contra `master.bib` y `documents/` agregando sufijo a, b, c...
  - [ ] Duplicado real (mismo DOI) no se resuelve aquí — lo maneja Storage Service

- [ ] Orchestrator — composición explícita de servicios; coordina el flujo completo de principio a fin
  - [ ] Chequeo de idempotencia: si el DOI ya existe en `master.bib` y el PDF ya está reubicado, log y salir sin reprocesar
  - [ ] DOI Service (given o from-PDF, según input disponible) -> hereda de Service Interface
  - [ ] MOD Resolution Service
  - [ ] Abstract Review Service
  - [ ] Key Generation Service
  - [ ] Storage Service (bib o clipboard) -> implementa Storage Interface
  - [ ] Relocator Service (mover PDF) -> implementa Relocator Interface
  - [ ] Orden de commit: validar todo primero (dry-run) -> mover PDF -> persistir entrada (bib/clipboard, con backup). Mover primero: si falla, no queda entrada huérfana en master.bib

## 5. storage
- [ ] Local Biblatex File Storage — implementa `Storage Interface` sobre master.bib
  - [ ] Check master.bib file
  - [ ] Make master.bib backup
  - [ ] Load master.bib into memory
  - [ ] Parse master.bib into python object
  - [ ] Duplicado por DOI/key ya existente -> raise error (el caso idempotente ya fue filtrado antes por el Orchestrator)
  - [ ] Append entry
  - [ ] Write atomically (archivo temporal + rename) — evita corromper `master.bib` si el proceso se interrumpe a medio escribir
  - [ ] Sin soporte de concurrencia: un solo proceso a la vez

- [ ] Local Clipboard Storage — implementa `Storage Interface` cuando master.bib no está disponible
  - [ ] Detectar entorno sin clipboard disponible (solo funciona en entorno local, no remoto/SSH sin forwarding)
  - [ ] Copy to clipboard

- [ ] Local Reallocate PDF file — implementa `Relocator Interface`
  - [ ] Check path existence
  - [ ] Create destination folder `documents/<AuthorYearMOD>/` si no existe 
  - [ ] Duplicate management (delega en Key Generation Service, no lógica propia)
  - [ ] Move and rename file from origin to destination usando el nombre canónico entregado por Key Generation Service (`AuthorSurnameYYYY-MOD.pdf`)

- [x] Local Storage File Checker
  - [x] Check if file exists
  - [x] Create empty file
  - [x] Rewrite file
  - [x] Raise configuration in case rewrite or create existing file

- [x] Local Storage Folder Checker
  - [x] Check if folder exists
  - [x] If not exist but create option flag is abled then create all path if is not existed
  - [x] Folders cannot be rewrited or erased


## Consideraciones

Backlog / futuro (no bloquea la implementación actual):

- **Análisis de abstract con Qwen local para tópico y relevancia** — a partir del abstract ya extraído (Abstract Review Service), sugerir automáticamente tópico y score de relevancia. Requeriría `Abstract Analyzer Interface` + adapter.
