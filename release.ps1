$version = python config.py

$Answer = Read-Host -Prompt "Release $version ? (y/n)"

if ($Answer -eq 'y' -or $Answer -eq 'Y') {
    git add config.py version.txt CHANGELOG.md
    git commit -m "update version to $version"
    git push
    git tag -a $version -m update
    git push --tags
} else {
    Write-Host "Aborted"
}