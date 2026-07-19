#! python

import subprocess

outputs = {
    'test01.svg': '1234n6789',
    'test02.svg': 'LPRPLKRK > WPWK > LP+RK RP+LK > [LPRK]',
    'test03.svg': '"[Text message.]"'
}

for output_file, command in outputs.items():
    print('===============================================================')
    print(f"Generating {output_file} for command: \"{command}\"")
    result = subprocess.run(['python', 'tekken_command_image.py', '-d', '-o', output_file, command], capture_output=True, text=True)
    print(f"Return code: {result.returncode}")
    print(result.stdout)
    print(result.stderr)

