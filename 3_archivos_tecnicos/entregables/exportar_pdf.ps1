# Exporta un .docx a PDF con Word. Uso: powershell -File exportar_pdf.ps1 "ruta\archivo.docx"
param([string]$Docx)
$pdf = [System.IO.Path]::ChangeExtension($Docx, ".pdf")
$w = New-Object -ComObject Word.Application
$w.Visible = $false
try {
  $d = $w.Documents.Open($Docx, $false, $true)
  $d.ExportAsFixedFormat($pdf, 17)
  "paginas: " + $d.ComputeStatistics(2)
  $d.Close($false)
} finally { $w.Quit() }
