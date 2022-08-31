# Shopee Tracker in CLI
Simple app to show spending on shopee website.

### Install Dependencies
```
pip install -r requirements.txt
```

### Usage
Rename `credential.ini.sample` to `credential.ini`.
Edit `credential.ini` by your editor.

```
[SHOPEE]
SPC_EC = your shopee cookies here
```

Execute python script.

```bash
python shopee.py

## Todo
- [x] Menu Selection
- [x] Purchase History
- [ ] Calculate Total
- [ ] Purchase History by Product

## License
Licensed under the [MIT license](http://opensource.org/licenses/MIT)