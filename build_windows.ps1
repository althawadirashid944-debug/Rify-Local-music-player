Write-Host "Installing Python dependencies..."

pip install -r requirements.txt
pip install pyinstaller


Write-Host "Creating build folders..."

New-Item -ItemType Directory -Force runtime\mpv | Out-Null
New-Item -ItemType Directory -Force dist | Out-Null


Write-Host "Extracting mpv runtime..."

7z x runtime\mpv\mpv.7z -oruntime\mpv -y


Write-Host "Building Rify..."

pyinstaller `
    --windowed `
    --onedir `
    --name Rify `
    --hidden-import=gi `
    --hidden-import=gi.repository.Gtk `
    --hidden-import=gi.repository.GLib `
    main.py


Write-Host "Copying mpv DLLs..."

Copy-Item runtime\mpv\*.dll dist\Rify\ -ErrorAction SilentlyContinue
Copy-Item runtime\mpv\**\*.dll dist\Rify\ -ErrorAction SilentlyContinue


Write-Host "Copying GTK runtime..."

Copy-Item runtime\gtk\bin\*.dll dist\Rify\ -ErrorAction SilentlyContinue -Recurse

Copy-Item runtime\gtk\share dist\Rify\share `
    -Recurse `
    -Force `
    -ErrorAction SilentlyContinue


Write-Host "Build finished!" 