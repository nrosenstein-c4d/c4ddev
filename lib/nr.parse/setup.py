
import io
import setuptools

with io.open('README.md') as fp:
  readme = fp.read()

with io.open('requirements.txt') as fp:
  requirements = fp.readlines()

setuptools.setup(
  name = 'nr.parse',
  version = '1.0.0',
  author = 'Niklas Rosenstein',
  author_email = 'rosensteinniklas@gmail.com',
  description = 'A simple text scanning/lexing/parsing library.',
  long_description = readme,
  long_description_content_type = 'text/markdown',
  url = 'https://github.com/NiklasRosenstein-Python/nr.parse',
  license = 'MIT',
  install_requires = requirements,
  packages = setuptools.find_packages('src'),
  package_dir = {'': 'src'}
)
