import ntpath
from pathlib import Path
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Progressbar

from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from pydub.silence import split_on_silence


def report_error(exc, val, tb):
    from traceback import TracebackException

    log = Path(Path().cwd(), "as.txt")

    with open(log, "w") as log:
        log.write("Exception in Tkinter callback")
        sys.last_type = exc
        sys.last_value = val
        sys.last_traceback = tb
        for line in TracebackException(type(val), val, tb, limit=None).format(
            chain=True
        ):
            log.write(line)
        log.write("\n")


class AudioSplitter:
    def __init__(self):
        self.title = "Audio Splitter"
        self.size = ""
        self.app = Tk()

        self.app.report_callback_exception = report_error

        self.app.title(self.title)
        self.app.geometry(self.size)

        self.formats = ["wav", "mp3"]
        self.current_format = StringVar(self.app)
        self.current_format.set("wav")

        self.source_path = StringVar(self.app)
        self.dest_path = StringVar(self.app)

        self.source_label = Label(
            self.app, text="Исходный файл дорожки", font=("Noto Sans", 13), padx=5
        )
        self.source_label.grid(row=1, column=0)

        self.source_input = Entry(
            self.app, textvariable=self.source_path, font=("Noto Sans", 13)
        )
        self.source_input.grid(row=1, column=1)

        self.source_browse = Button(
            self.app,
            text="Обзор",
            command=self.browse_source_button,
            font=("Noto Sans", 13),
            padx=5,
        )
        self.source_browse.grid(row=1, column=2)

        self.dest_label = Label(
            self.app, text="Выходная директория", font=("Noto Sans", 13), padx=5
        )
        self.dest_label.grid(row=2, column=0)

        self.dest_input = Entry(
            self.app, textvariable=self.dest_path, font=("Noto Sans", 13)
        )
        self.dest_input.grid(row=2, column=1)

        self.dest_browse = Button(
            self.app,
            text="Обзор",
            command=self.browse_dest_button,
            font=("Noto Sans", 13),
            padx=5,
        )
        self.dest_browse.grid(row=2, column=2)

        self.pause_label = Label(
            self.app,
            text="Длина паузы между фрагментами (в секундах)",
            font=("Noto Sans", 13),
            padx=5,
        )
        self.pause_label.grid(row=3, column=0)

        self.pause_input = Entry(self.app, font=("Noto Sans", 13))
        self.pause_input.grid(row=3, column=1)

        self.name_label = Label(
            self.app,
            text="Шаблон имени выходных файлов (к нему добавится порядковый номер)",
            font=("Noto Sans", 13),
            padx=5,
        )
        self.name_label.grid(row=4, column=0)

        self.name_input = Entry(self.app, font=("Noto Sans", 13))
        self.name_input.grid(row=4, column=1)

        self.format_label = Label(
            self.app, text="Формат выходных файлов", font=("Noto Sans", 13), padx=5
        )
        self.format_label.grid(row=5, column=0)

        self.format_input = OptionMenu(self.app, self.current_format, *self.formats,)
        self.format_input.grid(row=5, column=1)

        self.silence_label = Label(
            self.app,
            text="Пограничное значение тишины",
            font=("Noto Sans", 13),
            padx=5,
        )
        self.silence_label.grid(row=6, column=0)

        self.silence_input = Entry(self.app, font=("Noto Sans", 13))
        self.silence_input.grid(row=6, column=1)

        self.start = Button(
            self.app,
            text="Начать",
            font=("Noto Sans", 16),
            command=self.start_splitting,
            padx=5,
        )
        self.start.grid(row=7, column=1)

    def start_splitting(self):

        s_path = self.source_input.get()
        d_path = self.source_input.get()
        f_name = self.name_input.get()
        pause = self.pause_input.get()
        out_fmt = self.current_format.get()
        silence = self.silence_input.get() or -16

        fmt = s_path[-3:]
        name = f_name or ntpath.basename(s_path)

        if not s_path:
            messagebox.showerror(
                "Audio Splitter", "Путь до исходного файла не должен быть пустым"
            )
        if not s_path:
            messagebox.showerror(
                "Audio Splitter", "Путь до конечной директории не должен быть пустым"
            )
        if not pause:
            messagebox.showerror(
                "Audio Splitter", "Значение паузы не должно быть пустым"
            )
        if not re.match(r"^\d+$", pause):
            messagebox.showerror(
                "Audio Splitter", "Значение паузы должно содержать только число"
            )

        try:
            sound = AudioSegment.from_file(s_path, format=fmt)
        except CouldntDecodeError:
            messagebox.showerror("Audio Splitter", "Ошибка декодирования файла")
        else:
            chunks = split_on_silence(
                sound, min_silence_len=int(pause) * 1000, silence_thresh=int(silence),
            )
            percentage = 100 / len(chunks)
            bar = Progressbar(self.app, length=100)
            bar.grid(row=7, column=0)
            for i, chunk in enumerate(chunks):
                chunk.export(f"{d_path}/{name}_{i}.{out_fmt}", format=out_fmt)
                bar["value"] += percentage
            messagebox.showinfo("Audio Splitter", "Разделение завершено!")

    def browse_source_button(self):
        # Позволяет пользователю выбрать файл
        # и сохраняет путь до него в глобальной переменной source_path
        filename = filedialog.askopenfilename(
            filetypes=(
                ("Waveform Audio File Format", "*.wav"),
                ("MPEG-1 Audio Layer 3", "*.mp3"),
                ("Все файлы", "*.*"),
            )
        )
        self.source_path.set(filename)

    def browse_dest_button(self):
        # Позволяет пользователю выбрать директорию
        # и сохраняет путь до нее в глобальной переменной dest_path
        filename = filedialog.askdirectory()
        self.dest_path.set(filename)


def main():
    app = AudioSplitter()
    app.app.mainloop()


if __name__ == "__main__":
    main()
