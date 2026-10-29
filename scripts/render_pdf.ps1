param(
    [string]$PdfPath = $env:PDF_INPUT_PATH,
    [string]$OutputDir = $env:PDF_OUTPUT_DIR,
    [int]$MaxPages = 0
)

if ([string]::IsNullOrWhiteSpace($PdfPath)) {
    $PdfPath = $env:PDF_INPUT_PATH
}
if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = $env:PDF_OUTPUT_DIR
}

try {
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    $asTaskMethod = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Length -eq 1 -and $_.GetParameters()[0].ParameterType.Name -like 'IAsyncOperation*' } | Select-Object -First 1
    $asActionMethod = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Length -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncAction' } | Select-Object -First 1

    [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Pdf.PdfDocument, Windows.Data.Pdf, ContentType = WindowsRuntime] | Out-Null
    [Windows.Storage.Streams.InMemoryRandomAccessStream, Windows.Storage.Streams, ContentType = WindowsRuntime] | Out-Null

    if (!(Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    }

    $op1 = [Windows.Storage.StorageFile]::GetFileFromPathAsync($PdfPath)
    $file = $asTaskMethod.MakeGenericMethod([Windows.Storage.StorageFile]).Invoke($null, @($op1)).Result

    $op2 = [Windows.Data.Pdf.PdfDocument]::LoadFromFileAsync($file)
    $doc = $asTaskMethod.MakeGenericMethod([Windows.Data.Pdf.PdfDocument]).Invoke($null, @($op2)).Result

    $count = $doc.PageCount
    Write-Output "PAGE_COUNT:$count"

    $pagesToRender = $count
    if ($MaxPages -gt 0 -and $MaxPages -lt $count) {
        $pagesToRender = $MaxPages
    }

    for ($i = 0; $i -lt $pagesToRender; $i++) {
        $page = $doc.GetPage($i)
        $stream = New-Object Windows.Storage.Streams.InMemoryRandomAccessStream
        $renderOp = $page.RenderToStreamAsync($stream)
        $asActionMethod.Invoke($null, @($renderOp)).Wait()

        $bytes = New-Object byte[] $stream.Size
        $netStream = [System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($stream)
        $netStream.Read($bytes, 0, $bytes.Length) | Out-Null
        
        $outPath = Join-Path $OutputDir "page_$i.png"
        [System.IO.File]::WriteAllBytes($outPath, $bytes)
    }

    Write-Output "RENDER_SUCCESS:$pagesToRender"
} catch {
    Write-Error $_.Exception.Message
    exit 1
}
