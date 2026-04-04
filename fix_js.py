with open("app/static/app.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

idx = 0
for i, l in enumerate(lines):
    if "document.addEventListener('mousemove'" in l:
        idx = i + 4 # skip the block
        break

clean = lines[:idx]
clean.extend([
"        let baseRotationSpeed = 0.0015;\n",
"        function animate3D() {\n",
"            requestAnimationFrame(animate3D);\n",
"            targetRotationX = mouseY * 0.5; targetRotationY = mouseX * 0.5;\n",
"            mesh.rotation.y += baseRotationSpeed + (targetRotationY - mesh.rotation.y) * 0.05;\n",
"            mesh.rotation.x += baseRotationSpeed + (targetRotationX - mesh.rotation.x) * 0.05;\n",
"            renderer.render(scene, camera);\n",
"        }\n",
"        animate3D();\n",
"\n",
"        window.addEventListener('resize', () => {\n",
"            width = window.innerWidth;\n",
"            height = window.innerHeight;\n",
"            camera.aspect = width / height;\n",
"            camera.updateProjectionMatrix();\n",
"            renderer.setSize(width, height);\n",
"        });\n",
"\n",
"        window.setDragPhysics = function(isDragging) {\n",
"            if(isDragging) { wireMaterial.opacity = 0.9; baseRotationSpeed = 0.04; }\n",
"            else { wireMaterial.opacity = 0.45; baseRotationSpeed = 0.0015; }\n",
"        };\n",
"\n",
"        window.setResultsMode3D = function(inResults) {\n",
"            if(inResults) {\n",
"                wireMaterial.opacity = 0.05;\n",
"                baseRotationSpeed = 0.0002;\n",
"                mesh.scale.set(0.8, 0.8, 0.8);\n",
"            } else {\n",
"                wireMaterial.opacity = 0.45;\n",
"                baseRotationSpeed = 0.0015;\n",
"                mesh.scale.set(1, 1, 1);\n",
"            }\n",
"        };\n",
"    }\n",
"\n",
"})();\n"
])

with open("app/static/app.js", "w", encoding="utf-8") as f:
    f.writelines(clean)
