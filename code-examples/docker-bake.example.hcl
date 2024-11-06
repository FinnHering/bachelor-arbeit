
# Ein "target" ist eine konkrete Anweisung, wie ein (oder mehrere) Docker-Image(s) gebaut werden sollen.
target "platforms" {
  platforms = ["linux/amd64"]
}


# Eine "variable" ist ein Wert, der in mehreren Targets verwendet werden kann. Es kann über die Komandozeile beim ausführen von bake überschrieben werden.
variable "BASE_TAG" {
  default = "ghcr.io/finnhering/julea"
}


# Eine "group" ist eine Sammlung von Targets. Es kann verwendet werden, um mehrere Targets zusammenzufassen und alle auf einmal zu bauen.
group "ubuntu" {
  targets = ["ubuntu-spack"]
}

# Target build docker images with prebuild julea + dependencies using spack method
target "ubuntu-spack" {
  
  # Interner Name des Targets (muss gesetzt werden, wenn man matrix verwendet)
  name     = "julea-ubuntu-${versions}-04-spack-${compilers}"

  # Targets können untereinander erben. In diesem Fall erbt das Target "ubuntu-spack" die Eigenschaften von target "platforms"
  inherits = ["platforms"]
  
  # Matrix erlaubt es, ein Target mehrmals zu bauen, wobei alle möglichen Kombinationen von Werten in der Matrix verwendet werden. 
  matrix = {
    versions  = ["24", "22", "20"]
    compilers = ["gcc", "clang"]
  }

  # Argumente, die an das Dockerfile übergeben werden
  args = {
    UBUNTU_VERSION       = "${versions}.04"
    JULEA_SPACK_COMPILER = compilers
    CC                   = compilers
  }

  # Spezifiziert die Tags, die für das Docker-Image verwendet werden sollen
  tags       = ["${BASE_TAG}-spack:ubuntu-${versions}-04-${compilers}"]

  # Spezifiziert den stage der Dockerfile, die für das Image benutzt werden soll
  target     = "julea"

  # Spezifiziert den Pfad zum Dockerfile
  dockerfile = "Dockerfile.example"
}