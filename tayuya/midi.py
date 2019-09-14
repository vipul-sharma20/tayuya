from typing import List, Dict, Iterator, Tuple

import mido
from mido import MidiFile
from music21 import note as musicnote
from music21 import stream, analysis, pitch

from tayuya import constants
from tayuya.tabs import Tabs
from tayuya.exceptions import TrackError


class MIDIParser:
    """
    MIDI file parser

    :param file_path: MIDI file path
    :param track: Track number in the MIDI file to be picked

    Example:

    >>> from tayuya import MIDIParser
    >>> mid = MIDIParser('sample.mid', track=0)
    >>> mid.render_tabs()

    Don't forget to set the `track` argument with the appropriate track
    number desired.
    """

    def __init__(self, file_path: str, track=0):
        self.midi_file = MidiFile(file_path)

        self.track = track
        self.midi_data = self.midi_file.tracks[track]

        # Get time signature
        ts_meta = list(filter(lambda x: x.type == constants.TIME_SIGNATURE,
                              self.midi_data))
        if ts_meta:
            numerator = ts_meta[0].numerator
            denominator = ts_meta[0].denominator
        else:
            numerator = denominator = 4
        self.time_signature = (numerator, denominator)

        self.stream = stream.Stream()

        if not self.midi_data:
            raise TrackError

    def notes_played(self) -> List[Dict]:
        """
        Get all notes played in this MIDI track

        :returns: List of all notes player with note time
        """
        return [
            dict(note=self._midi_to_note(note.note), time=note.time)
            for note in self._on_note()
        ]

    def get_tracks(self) -> Dict:
        """
        Get all tracks of the MIDI file

        :returns: track number and name mapping
        """
        return {idx: track.name for idx, track in enumerate(self.midi_file.tracks)}

    def get_key(self) -> pitch.Pitch:
        """
        Get key of this MIDI track

        refer: http://web.mit.edu/music21/doc/moduleReference/moduleAnalysisDiscrete.html

        We have used Krumhansl-Schmuckler algorithm for key determitination with
        following weightings implementation:

        * Aarden-Essen
        * Bellman-Budge
        * Krumhansl-Schmuckler
        * Krumhansl-Kessler
        * Temperley-Kostka-Payne

        Key which is determined the most by these methods is chosen

        :returns: predicted key of a MIDI track
        """
        note_length: float = 0.0

        for note in self.midi_data:
            if note.type not in [constants.NOTE_ON, constants.NOTE_OFF] or note.is_meta:
                continue
            note_length += note.time
            if note.type == constants.NOTE_ON:
                self.stream.append(musicnote.Note(note.note,
                                   type=self._get_note_type(note_length)))
                note_length = 0.0

        key_weight = analysis.discrete.KeyWeightKeyAnalysis().process(self.stream)
        krumhansl_shmuckler = analysis.discrete.KrumhanslSchmuckler().process(self.stream)
        bellman_budge = analysis.discrete.BellmanBudge().process(self.stream)
        aarden_essen = analysis.discrete.AardenEssen().process(self.stream)
        krumhansl_kessler = analysis.discrete.KrumhanslKessler().process(self.stream)
        temperley_kostka_payne = analysis.discrete.TemperleyKostkaPayne().process(self.stream)

        prediction = list(map(lambda x: (x[0][0], x[0][1]),
                              [key_weight, krumhansl_shmuckler, bellman_budge,
                               aarden_essen, krumhansl_kessler,
                               temperley_kostka_payne]))

        return max(prediction, key=prediction.count)

    def render_tabs(self, **kwargs) -> None:
        """
        Visualize notes in tabulature format
        """
        tabs = Tabs(notes=self.notes_played(), key=self.get_key())
        to_play = tabs.generate_notes()

        tabs.render(to_play, **kwargs)

    def _on_note(self) -> Iterator:
        """
        Filter all notes which are `on`

        :returns: List of notes which were on
        """
        return filter(
            lambda x: x.type == constants.NOTE_ON, self.midi_data)

    def _midi_to_note(self, midi_note: int) -> str:
        """
        Convert MIDI note to music note

        :param midi_note: MIDI code for this note

        :returns: String notation of MIDI note
        """
        return constants.MIDI_TO_NOTES[midi_note][0]

    def _get_note_type(self, note_length: int) -> str:
        """
        Get note type: `quarter`, `half`, `whole`, `eighth` or `sixteenth`

        :params note_length: length of this note played

        :returns: Type of note played
        """
        num_beats = note_length / self.midi_file.ticks_per_beat

        # Get which note type gets the beat
        beat_note = constants.NUM_TO_NOTES[self.time_signature[1]]

        if num_beats <= 1.5:
            return beat_note
        elif 1.5 < num_beats <= 2.5:
            return constants.NUM_TO_NOTES[self.time_signature[1] // 2]
        else:
            return constants.WHOLE_NOTE

