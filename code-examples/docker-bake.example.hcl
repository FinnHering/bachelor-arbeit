target "platforms" {
  platforms = ["linux/amd64"]
}

variable "BASE_TAG" {
  default = "ghcr.io/finnhering/julea"
}

group "ubuntu" {
  targets = ["ubuntu-spack"]
}

# Target build docker images with prebuild julea + dependencies using spack method
target "ubuntu-spack" {
  name     = "julea-ubuntu-${versions}-04-spack-${compilers}"
  inherits = ["platforms"]
  matrix = {
    versions  = ["24", "22", "20"]
    compilers = ["gcc", "clang"]
  }
  args = {
    UBUNTU_VERSION       = "${versions}.04"
    JULEA_SPACK_COMPILER = compilers
    CC                   = compilers
  }

  # Add -dependencies to the tag if the target is julea_dependencies
  tags       = ["${BASE_TAG}-spack:ubuntu-${versions}-04-${compilers}"]
  target     = "julea"
  dockerfile = "Dockerfile.example"
}