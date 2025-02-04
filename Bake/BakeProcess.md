# Bake Process

## Scene Settings [DONE]

- Render Engine -> "Cycles"
- Device -> "GPU Compute"
- Bake
  - Bake Type -> "Diffuse"
  - Contributions -> Only Check "Colors" -> Uncheck "Direct" & "Indirect"
  - Margin -> 0px

## Actual Process [WIP]

- Select a mesh
- Go to Shader Editor
  - Create Image Texture
    - Set the name same as mesh name
    - Set the resolution to 16K (for now 1K works)
- Go to Image Editor
  - Create Image Tile with the same UDIM number as the image name
  - Delete the default tile 1001
- Click Bake
