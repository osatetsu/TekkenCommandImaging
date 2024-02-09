# Tekken game command imager

This tool generate png-image from "command".
That command is used fighting game "Tekken" series.

## Install / Requirement

Please install python 3.12 or later.
If you using Windows 10/11, you can find it on Microsoft store.

And, install modules.

```.sh
pip install -r requirements.txt
```

## Usage

Run command on your terminal.

```.sh
python tekken_command_image.py -o <output.png> 'commands'
```

Feature:

 * Commands are supporting Tenkey-style.
    * Directional `1234n6789`. See below.
    * Button `LP, RP, WP, LK, RK, WK`
    * Ignore cases. You can use both uppercase and lowercase.
    * Use `+` to press multiple buttons at the same time.
    * Slide syntax `[ ]` 
    * Command delimiter are `>` or `,`
    * You can use ` ` (white space). To improve visibility.

Directional-key and buttons:

```
 7 8 9   LP RP (Both punch is 'WP')
 4 n 6 
 1 2 3   LK RK (Both kick is 'WK')
```

![dir and buttun](images/dir-button.png)

### Example No.1: Fujin-ken

```.sh
python tekken_command_image.py -o images/fujinken.png '6n23RK'
```

![Fujin-ken](images/fujinken.png)

### Example No.2: Zenshippo - Tekken 7

```.sh
python tekken_command_image.py -o images/zenshippo.png '6[lklp]'
```

![Zenshippo](images/zenshippo.png)

### Example No.3: Nina combo

```.sh
python tekken_command_image.py -o output.png '3RP > 9RK > 9LK > 3LKRP1RP > 66 > 3LKRP4RK > 66 > 236RKLKWP' 
```

![Nina combo](images/nina_combo.png)

### Example No.4: Bryan "Fury"

Pressing multiple buttons at the same time.
But I don't know if it's possible in Tekken 8 as well.

```.sh
python tekken_command_image.py -d -o bryan_combo.png 'LP+LK + RK > 64RP'
```

![Bryan combo](images/bryan_combo.png)

## License

Source code and documents are GPLv3.

## Notification

 * If you have any requests for additional features or report bugs, please submit them to [Issues](https://github.com/osatetsu/TekkenCommandImaging/issues).
 * If you can donate through ko-fi, it will encourage my activities.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/E1E1U0BU1)
