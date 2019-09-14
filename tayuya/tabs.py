from typing import Dict, Tuple, List

from music21 import scale

from tayuya import constants


class Tabs:
    """
    Tab generator
    """

    def __init__(self, notes: List[Dict], key: Tuple):
        self.notes = notes
        self.key = key
        self.notes_cache: Dict = {}

    def generate_notes(self) -> List[Tuple[str, int, int]]:
        """
        Get list of all notes to play with their fret and string positions

        :param start_from: (fret, string, scale_notes), start position of the tab

        :returns: (note, string, fret) list of notes to play
        """
        fret, _, scale_notes = self.find_start()
        to_play: List = []

        for note in self.notes:
            note_fret, note_string = self.note_nearest_to_fret(fret, note['note'], scale_notes)
            to_play.append((note['note'], note_string, note_fret))
            fret = note_fret

        return to_play

    def note_nearest_to_fret(self, fret: int, note: str, scale_notes: List[Tuple]) -> Tuple[int, int]:
        """
        Find best position (fret and string) for a note

        :param fret: fret position (last fret played)
        :param note: note to find position for
        :param scale_notes: (note, fret, string) for all notes in the detected scale

        :returns: best (fret, string) pair for a note
        """
        try:
            note_info = constants.NOTE_TO_STRING[note]
        except:
            try:
                if int(note[-1]) <= 2:
                    new_note = note[:-1] + '3'
                    note_info = constants.NOTE_TO_STRING[new_note]
            except ValueError:
                pass

        min_fret = min_string = min_diff = 999

        for note_string, note_fret in note_info.items():
            if not note_fret:
                continue

            if (note_fret, note_string) in scale_notes:
                return (note_fret, note_string)

            if self.notes_cache.get(note):
                return self.notes_cache[note]

            diff = abs(note_fret - fret)
            if diff <= min_diff:
                min_diff = diff
                min_fret = note_fret
                min_string = note_string

        self.notes_cache[note] = (min_fret, min_string)

        return (min_fret, min_string)

    def find_start(self) -> Tuple[int, int, List[Tuple]]:
        """
        Find start position of the tab

        :param start_fret: Starting fret of this scale

        :returns: (fret, string, all notes in this scale)
        """
        max_count: int = 0
        start_fret = start_string = 0
        start_scale_notes: List = []

        # (pitch, scale_type)
        pitch, scale_type = self.key
        pitch = self._fix_note_name(pitch)
        this_scale_step = constants.SCALE[scale_type]

        sc = self._get_scale()

        this_scale_notes = [note.nameWithOctave for note in sc.pitches]
        first_note = this_scale_notes[0]

        note_info = constants.NOTE_TO_STRING[self._fix_note_name(first_note)]

        for note_string, note_fret in note_info.items():
            string: int = note_string
            fret: int = note_fret
            num_notes: int = 0
            step: int = 0
            span: int = 8
            note_list: List = [(fret, string)]

            while string > 0 and span > 0 and note_fret:
                fret += this_scale_step[step]
                step += 1
                num_notes += 1
                note_list.append((fret, string))

                if step >= len(constants.SCALE[scale_type]):
                    step = 0
                if fret > note_fret + 3:
                    fret -= 4 if string == 2 else 5
                    string -= 1
                if num_notes > max_count:
                    max_count = num_notes
                    start_fret = note_fret
                    start_string = note_string
                    start_scale_notes = note_list

                span -= 1

        return start_fret, start_string, start_scale_notes

    def render(self, notes_list: List[Dict], **kwargs) -> None:
        """
        Render guitar tabs in CLI

        :param note_list: List of notes to play with fret and string positions

        :returns: None
        """
        staff_length = kwargs.get('staff_length', constants.MAX_RENDER_COLUMNS)
        fretboard = ['' for _ in range(constants.GUITAR_STRING)]

        for note, note_string, note_fret in notes_list:
            idx_note_string = int(note_string) - 1

            # If fretboard string's length is greater than the current note's
            # string then, find diff and equalize the lenght of both
            for idx, fretboard_string in enumerate(fretboard):
                if len(fretboard_string) > len(fretboard[idx_note_string]):
                    diff = len(fretboard_string) - len(fretboard[idx_note_string])
                    fretboard[idx_note_string] += f'{constants.TAB_LINE_CHAR}' * diff

            # Insert note in appropriate string on the fretboard
            fret = str(note_fret)
            fretboard[idx_note_string] += f'{constants.TAB_LINE_CHAR}{fret}{constants.TAB_LINE_CHAR}'

        max_staff_length = len(max(fretboard, key=len))

        for idx, string in enumerate(fretboard):
            diff = max_staff_length - len(string)
            fretboard[idx] = fretboard[idx] + constants.TAB_LINE_CHAR * diff

        break_point = staff_length

        for string in fretboard:
            if string[break_point] != constants.TAB_LINE_CHAR:
                break_point += 1
                continue

        string_idx = 0
        start = 0
        end = break_point
        while True:
            if not fretboard[string_idx][start:] and start > staff_length:
                break
            for idx, string in enumerate(fretboard):
                print(constants.GUITAR_STAFF[idx] + string[start:end])

            string_idx += 1
            string_idx = string_idx % constants.GUITAR_STRING
            start = end
            end = start + break_point

            print()

    def _fix_note_name(self, pitch) -> str:
        """
        Fix note name generated by music21

        :returns: Name of the note
        """
        if isinstance(pitch, str):
            name = pitch
        else:
            name = pitch.nameWithOctave
        name = name.replace('-', 'b')
        try:
            int(name[-1])
        except ValueError:
            name += str(pitch.implicitOctave)
        return name

    def _get_scale(self):
        """
        Get music21 scale for a scale type

        :param scale_type: major, minor, dorian etc.
        """
        pitch, scale_type = self.key

        if scale_type in [constants.MAJOR, constants.IONIAN]:
            return scale.MajorScale(pitch)
        elif scale_type in [constants.MINOR, constants.AEOLIAN]:
            return scale.MinorScale(pitch)
        elif scale_type == constants.DORIAN:
            return scale.DorianScale(pitch)
        elif scale_type == constants.PHRYGIAN:
            return scale.PhrygianScale(pitch)
        elif scale_type == constants.LYDIAN:
            return scale.LydianScale(pitch)
        elif scale_type == constants.LOCRIAN:
            return scale.LocrianScale(pitch)
        else:
            return scale.MajorScale(pitch)
