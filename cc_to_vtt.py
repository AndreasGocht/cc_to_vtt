import argparse
import datetime


class frame:
    def __init__(self, text, begin, end=None):
        self.begin = begin
        self.text = text
        self.end = end

    def __str__(self) -> str:
        out = "{}.000 --> {}.000\n".format(
            self.begin, self.end)
        out += self.text
        return out

    def split(self):
        diff = self.end - self.begin
        diff = diff / 2
        diff = datetime.timedelta(seconds=diff.seconds)

        if diff < datetime.timedelta(seconds=1):
            raise RuntimeError("to smal")

        max_search = int(len(self.text)/2)
        sep = self.text.rfind(" ", 0, max_search)
        text1 = self.text[:sep] + "\n"
        text2 = self.text[sep+1:]

        f1 = frame(text=text1,
                   begin=self.begin,
                   end=self.begin + diff)
        f2 = frame(text=text2,
                   begin=self.begin + diff,
                   end=self.end)
        return (f1, f2)


"""
00:01.000 --> 00:04.000
- Never drink liquid nitrogen.
"""

parser = argparse.ArgumentParser(
    description='Parse closed Captions and create VTT.')
parser.add_argument('--input', type=str, nargs="?", metavar="<path>",
                    help='CC file to be parsed')
parser.add_argument('--output', type=str, nargs="?", metavar="<path>",
                    help='VTT file to be saved')
parser.add_argument('--end', type=str, nargs="?", metavar="<path>",
                    help='ending for the last vtt line')


args = parser.parse_args()

if not args.output.endswith(".vtt"):
    raise ValueError("file does not end with .vtt")

# https://developer.mozilla.org/en-US/docs/Web/API/WebVTT_API


with open(args.input) as f:
    data = f.readlines()

begin = None
frames = []
for line in data:
    timestamp = line[:8]
    text = line[9:]
    timestamp = datetime.timedelta(hours=int(timestamp[0:2]),
                                   minutes=int(timestamp[3:5]),
                                   seconds=int(timestamp[6:8]))
    if begin is None:
        begin = timestamp
        frame_begin = timestamp - begin
    else:
        frame_begin = timestamp - begin
        frames[-1].end = frame_begin
    frames.append(frame(text, frame_begin))

timestamp_end = datetime.timedelta(hours=int(args.end[0:2]),
                                   minutes=int(args.end[3:5]),
                                   seconds=int(args.end[6:8]))


assert timestamp_end > frames[-1].begin
frames[-1].end = timestamp_end

short_frames = []


def split_frame(fr):
    if len(fr.text) > 100:
        f1, f2 = fr.split()
        ret = []
        ret.extend(split_frame(f1))
        ret.extend(split_frame(f2))
        return ret
    else:
        return [fr]


short_frames = []
for fr in frames:
    fs = split_frame(fr)
    short_frames.extend(fs)


with open(args.output, "w") as ouf:
    ouf.write("WEBVTT \n")
    ouf.write("\n")
    for frame in short_frames:
        ouf.write(str(frame))
        ouf.write("\n")
