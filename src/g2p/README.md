
## Grapheme-to-phoneme aka g2p aka phonemizer

Use this code to create a phonetic dictionary or lexicon. The input is a vocabulary word list, the output is list of {vocabulary words, phonetic spelling} in both IPA and XSAMPA


## Setup

 - Make a virtual environment
 - Activate it
 - Install all requirements

```
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```


## Run
```
(venv) $ python g2p.py raw_vocab.txt
```

The output is generated and written to the console as so: grapheme `....` IPA `....` XSAMPA

```
...
aláǹtakùn       aláǹtakùn      a l a_H n_L t a k u_L n
aláṣe       aláʃe      a l a_H S e
aláṣepọ̀       aláʃek͡pɔ̀      a l a_H S e kp O_L
aláṣẹ       aláʃɛ      a l a_H S E
alè       alè      a l e_L
alòbá       alòbá      a l o_L b a_H
alóhun       alóhũ      a l o_H h u~
alóńgẹ       alóńɡɛ      a l o_H n_H g E
alẹsinlọyẹ       alɛsĩlɔjɛ      a l E s i~ l O j E
alẹ̀       alɛ̀      a l E_L
alẹ́       alɛ́      a l E_H
alọ́ba       alɔ́ba      a l O_H b a
ama       ama      a m a
amadi       amadi      a m a d i
ami       ami      a m i
amojútó       amod͡ʒútó      a m o dZ u_H t o_H
amoye       amoje      a m o j e
amáyédẹrùn       amájédɛrùn      a m a_H j e_H d E r u_L n
amáyédẹ̀rún       amájédɛ̀rún      a m a_H j e_H d E_L r u_H n
...
```



