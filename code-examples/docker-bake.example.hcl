# Ein "target" ist eine konkrete Anweisung, wie ein (oder mehrere) Docker-Image(s) gebaut werden sollen.
target "platforms" { platforms = ["linux/amd64"] }

# Mit hilfe von Variablen kann man beim aufrufen über die Kommandozeile Werte übergeben
variable "BASE_TAG" { default = "example/example-container" }

# Eine "group" ist eine Sammlung von Targets. Es kann verwendet werden, um mehrere Targets zusammenzufassen und alle auf einmal zu bauen.
group "ubuntu" { targets = ["ubuntu"] }

target "ubuntu" {
  # Interner Name des Targets ist pflicht, bei matrix targets
  name = "ubuntu-${versions}-04"

  # Targets können untereinander erben. In diesem Fall erbt das Target "ubuntu-spack" die Eigenschaften von target "platforms"
  inherits = ["platforms"]
  
  # Matrix erlaubt es, ein Target mehrmals zu bauen, wobei alle möglichen Kombinationen von Werten in der Matrix verwendet werden. 
  matrix = { versions  = ["24", "22", "20"] }

  # Argumente, die an das Dockerfile übergeben werden
  args = { UBUNTU_VERSION = "${versions}.04" }

  # Spezifiziert die Tags, die für das Docker-Image verwendet werden sollen
  tags = ["${BASE_TAG}:ubuntu-${versions}-04"]

  # Spezifiziert den stage der Dockerfile, die für das Image benutzt werden soll
  target = "production"

  # Spezifiziert den Pfad zum Dockerfile
  dockerfile = "Dockerfile"
}