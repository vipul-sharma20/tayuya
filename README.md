# Tayuya

A tool to generate guitar tabs from MIDI files

Live demo: [midi.vipul.xyz](http://midi.vipul.xyz)

# Installation

`pip install tayuya`

# Usage

```python
In [1]: from tayuya import MIDIParser

In [2]: mid = MIDIParser('sample.mid', track=0)

In [3]: mid.render_tabs()
Out[3]:
```
```
E-------------14--------------------------16--14----------14--------------
A-------------------------------------------------17--17------16--17--16--
D-16------16------16--16--16--16------16----------------------------------
G-----18--------------------------18--------------------------------------
B-------------------------------------------------------------------------
E-------------------------------------------------------------------------
```

***Don't forget to set the `track` argument with the appropriate track number desired.***

### Get track numbers of all the tracks in the MIDI file

```python

In [1]: from tayuya import MIDIParser

In [2]: mid = MIDIParser('sample.mid', track=0)

In [3]: mid.get_tracks()
Out[3]:
{0: 'Lead Guitar',
 1: 'Rhthym Guitar Dist',
 2: 'Acoustic Guitar',
 3: 'Rhthym Guitar Clean & Dist',
 4: 'Lead Guitar Fill',
 5: 'Guitar Harmonics',
```

# Advanced

## MIDI

### Get all notes played in the MIDI track

```python
In [1]: mid = MIDIParser('sample.mid', track=0)

In [2]: mid.notes_played()
Out[2]:
[{'note': 'C#5', 'time': 18},
 {'note': 'C#5', 'time': 30},
 {'note': 'B4', 'time': 26},
 {'note': 'C5', 'time': 0},
 {'note': 'C5', 'time': 28},
 {'note': 'C#5', 'time': 28},
 {'note': 'C#5', 'time': 30}]
```

### Get key of the track

```python
In [1]: mid = MIDIParser('sample.mid', track=0)

In [2]: mid.get_key()
```

## Tabs

### Get all notes to play

You can use this example to generate all the notes to play with their string
and fret positions.

```python
In [1]: mid = MIDIParser('sample.mid', track=0)

In [2]: tabs = Tabs(notes=mid.notes_played(), key=mid.get_key())

In [3]: tabs.generate_notes(tabs.find_start())
Out[3]:
[('C#3', 5, 4),
 ('G#3', 4, 6),
 ('C#4', 3, 6),
 ('F4', 2, 6),
 ('B2', 6, 7),
 ('D#3', 5, 6),
 ('F#3', 4, 4),
 ('B3', 3, 4),
 ('D#4', 3, 8),
 ('F#2', 6, 2)]
```

Each tuple here is `(note, string, fret)`

# How it works?

Here's a brief of how it works:

* Fetch a track from the MIDI file
* Find all the notes played and convert from MIDI code values to music notes
* Find a scale for the set of notes extracted
* Find the best position to play the extracted notes using the scale detected

# Limitations

* Works only for guitar solos. Implementation for determination and rendering of
  chords is not done yet.
* Works only for standard tuning (E A D G B E)

# TODO

- [ ] Render tabs using Lilypond or some GUI alternative
- [ ] Implement logic to determine and render chords
- [ ] Better the scale detection implementation
- [ ] Transposing
- [ ] Add way to handle non standard tuning
- [ ] More stringed instruments

# LICENSE

[MIT](https://github.com/vipul-sharma20/tayuya/blob/master/)

# Credits

Tayuya is made possible by following open source softwares:

* [Mido](https://github.com/mido/mido)
* [Music21](https://github.com/cuthbertLab/music21)

# The name

[Tayuya](https://naruto.fandom.com/wiki/Tayuya) (たゆや)

