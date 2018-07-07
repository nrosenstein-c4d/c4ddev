
import io
import setuptools

with io.open('README.md', encoding='utf8') as fp:
  readme = fp.read()

with io.open('requirements.txt') as fp:
  requirements = fp.readlines()

setuptools.setup(
  name = 'nr.types',
  version = '1.0.5',
  author = 'Niklas Rosenstein',
  author_email = 'rosensteinniklas@gmail.com',
  description = 'Anything related to Python datatypes.',
  long_description = readme,
  long_description_content_type = 'text/markdown',
  url = 'https://gitlab.niklasrosenstein.com/NiklasRosenstein/python/nr.types',
  license = 'MIT',
  packages = setuptools.find_packages('src'),
  package_dir = {'': 'src'},
  install_requires = requirements
)
