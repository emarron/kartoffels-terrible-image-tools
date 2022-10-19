from pathlib import Path

references_path = Path('./reference')
inputs_path = Path('./input')
reference_list = list(references_path.glob('**/*.*'))
input_list = list(inputs_path.glob('**/*.*'))

for path in input_list:
    print(Path.joinpath(Path('D0G'), (path.relative_to(*path.parts[:1]).with_name(path.stem + ".cat"))))
