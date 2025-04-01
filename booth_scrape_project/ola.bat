$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    model = "gemma3:12b"
    prompt = "こんにちは！"
    stream = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Headers $headers -Body $body