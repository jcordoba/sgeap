## ADDED Requirements

### Requirement: Upload Evidence
The system SHALL allow users to upload files as evidence associated to a fase or specific field.

#### Scenario: Upload evidence to fase
- **GIVEN** fase exists
- **WHEN** user uploads file via POST /api/fases/{id}/evidencias
- **THEN** system stores file to storage
- **AND** system creates evidencia record with ruta_storage
- **AND** system returns evidencia with id and download URL

#### Scenario: Upload evidence to specific field
- **GIVEN** fase and campo exist
- **WHEN** user uploads file with campo_id
- **THEN** system associates evidencia to both fase and campo

---

### Requirement: Evidence File Types
The system SHALL accept the following file types:
- PDF (.pdf)
- Word documents (.doc, .docx)
- Excel spreadsheets (.xls, .xlsx)
- Images (.jpg, .jpeg, .png)
- Compressed archives (.zip)

Maximum file size: 50MB

#### Scenario: Reject invalid file type
- **GIVEN** user uploads file with invalid extension
- **WHEN** system validates file
- **THEN** system returns 400 Bad Request with error message

#### Scenario: Reject oversized file
- **GIVEN** user uploads file larger than 50MB
- **WHEN** system validates file
- **THEN** system returns 413 Payload Too Large

---

### Requirement: List Evidence
The system SHALL return all evidence for a fase.

#### Scenario: List fase evidence
- **GIVEN** fase has associated evidencias
- **WHEN** user requests GET /api/fases/{id}/evidencias
- **THEN** system returns list with: id, nombre_archivo, tipo_mime, tamano_bytes, uploaded_by, created_at

---

### Requirement: Download Evidence
The system SHALL allow authorized users to download evidence files.

#### Scenario: Download evidence
- **GIVEN** evidencia exists
- **WHEN** user requests GET /api/evidencias/{id}/download
- **THEN** system returns file as attachment
- **AND** Content-Disposition header contains original filename

---

### Requirement: Delete Evidence
The system SHALL allow deletion of evidence only if fase estado allows editing.

#### Scenario: Delete evidence
- **GIVEN** evidencia exists on fase with estado=BORRADOR
- **WHEN** user calls DELETE /api/evidencias/{id}
- **THEN** system deletes file from storage
- **AND** system deletes evidencia record
- **AND** system creates audit log entry

#### Scenario: Cannot delete evidence on locked fase
- **GIVEN** evidencia exists on fase with estado=APROBADO
- **WHEN** user tries to delete evidencia
- **THEN** system returns 403 Forbidden