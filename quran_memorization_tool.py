#!/usr/bin/env python3
"""
Quran Memorization Practice Tool
GUI application for practicing Quran recitation with speech recognition
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import csv
import difflib
import speech_recognition as sr
import threading
import pygame
import os
import sys
import time
import re
import unicodedata


class QuranMemorizationTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Quran Memorization Practice Tool")
        self.root.geometry("800x700")
        self.root.configure(bg="#f0f0f0")
        
        pygame.mixer.init()
        
        self.microphoneAvailable = False
        self.recognizer = None
        self.microphone = None
        
        try:
            import pyaudio
            pyaudioAvailable = True
        except ImportError:
            pyaudioAvailable = False
            print("Warning: PyAudio not found. Microphone features will be disabled.")
        
        try:
            self.recognizer = sr.Recognizer()
        except Exception as e:
            print(f"Warning: Error initializing recognizer: {str(e)}")
            self.recognizer = None
        
        if pyaudioAvailable:
            try:
                self.microphone = sr.Microphone()
                self.microphoneAvailable = True
            except Exception as e:
                print(f"Warning: Error initializing microphone: {str(e)}")
                self.microphoneAvailable = False
        else:
            self.microphoneAvailable = False
        
        self.isListening = False
        self.currentAyahIndex = 0
        self.currentSurah = None
        self.ayahList = []
        self.startAyah = 1
        self.endAyah = 1
        self.accumulatedRecitation = ""
        self.listeningMode = "surah"
        self.currentAyahCompleted = False
        self.surahNameMapping = self.createSurahNameMapping()
        
        self.quranData = {}
        self.loadQuranData()
        self.setupGUI()
        
        if self.microphoneAvailable:
            self.calibrateMicrophone()
        else:
            if hasattr(self, 'feedbackLabel'):
                self.feedbackLabel.config(
                    text="⚠️ PyAudio not installed. Microphone features disabled.",
                    fg="#e74c3c"
                )
    
    def createSurahNameMapping(self):
        mapping = {}
        numberWords = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
            "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
            "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100, "first": 1, "second": 2, "third": 3
        }
        
        for num in range(1, 115):
            mapping[str(num)] = num
            if num in numberWords.values():
                for word, val in numberWords.items():
                    if val == num:
                        mapping[word] = num
        
        commonSurahNames = {
            "الفاتحة": 1, "فاتحة": 1, "سورة الفاتحة": 1,
            "البقرة": 2, "بقرة": 2, "سورة البقرة": 2,
            "آل عمران": 3, "عمران": 3, "سورة آل عمران": 3,
            "النساء": 4, "نساء": 4, "سورة النساء": 4,
            "المائدة": 5, "مائدة": 5, "سورة المائدة": 5,
            "al-fatiha": 1, "fatiha": 1, "al fatiha": 1, "the opening": 1,
            "al-baqarah": 2, "baqarah": 2, "al baqarah": 2, "the cow": 2,
            "al-imran": 3, "imran": 3, "al imran": 3, "family of imran": 3,
            "an-nisa": 4, "nisa": 4, "an nisa": 4, "the women": 4,
            "al-maidah": 5, "maidah": 5, "al maidah": 5, "the table": 5,
        }
        mapping.update(commonSurahNames)
        
        return mapping
    
    def loadQuranData(self):
        csvFilePath = "quran.csv"
        try:
            if not os.path.exists(csvFilePath):
                messagebox.showerror("Error", f"File {csvFilePath} not found.")
                return
            
            with open(csvFilePath, 'r', encoding='utf-8') as csvFile:
                csvReader = csv.DictReader(csvFile)
                for row in csvReader:
                    surahNum = int(row['surah'])
                    ayahNum = int(row['ayah'])
                    text = row['text'].strip()
                    
                    if surahNum not in self.quranData:
                        self.quranData[surahNum] = {}
                    self.quranData[surahNum][ayahNum] = text
            
            print(f"Loaded {len(self.quranData)} surahs from {csvFilePath}")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading Quran data: {str(e)}")
    
    def calibrateMicrophone(self):
        if not self.microphoneAvailable:
            return
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Microphone calibrated")
        except Exception as e:
            print(f"Warning: Could not calibrate microphone: {str(e)}")
    
    def setupGUI(self):
        titleLabel = tk.Label(
            self.root,
            text="Quran Memorization Practice Tool",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        titleLabel.pack(pady=10)
        
        inputFrame = tk.Frame(self.root, bg="#f0f0f0")
        inputFrame.pack(pady=10)
        
        self.startButton = tk.Button(
            inputFrame,
            text="Start Listening for Surah",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            command=self.startListeningForSurah,
            width=20,
            height=2
        )
        self.startButton.pack(padx=10, pady=5)
        
        correctFrame = tk.LabelFrame(
            self.root,
            text="Correct Verse",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        correctFrame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.correctText = scrolledtext.ScrolledText(
            correctFrame,
            font=("Arial", 16),
            height=4,
            wrap=tk.WORD,
            bg="#ffffff",
            fg="#2c3e50",
            state=tk.DISABLED
        )
        self.correctText.pack(padx=10, pady=10, fill="both", expand=True)
        
        recitedFrame = tk.LabelFrame(
            self.root,
            text="Your Recitation (Real-time)",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        recitedFrame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.recitedText = scrolledtext.ScrolledText(
            recitedFrame,
            font=("Arial", 16),
            height=4,
            wrap=tk.WORD,
            bg="#ecf0f1",
            fg="#34495e"
        )
        self.recitedText.pack(padx=10, pady=10, fill="both", expand=True)
        
        initialText = "Click 'Start Listening for Surah' and say the surah name to begin"
        if not self.microphoneAvailable:
            initialText = "⚠️ PyAudio not installed. Install with: brew install portaudio && pip3 install pyaudio"
        self.feedbackLabel = tk.Label(
            self.root,
            text=initialText,
            font=("Arial", 14),
            bg="#f0f0f0",
            fg="#7f8c8d" if self.microphoneAvailable else "#e74c3c",
            wraplength=750
        )
        self.feedbackLabel.pack(pady=10)
        
        controlFrame = tk.Frame(self.root, bg="#f0f0f0")
        controlFrame.pack(pady=10)
        
        self.stopButton = tk.Button(
            controlFrame,
            text="Stop Listening",
            font=("Arial", 12),
            bg="#e74c3c",
            fg="white",
            command=self.stopListening,
            width=15,
            state=tk.DISABLED
        )
        self.stopButton.pack(side=tk.LEFT, padx=5)
    
    def startListeningForSurah(self):
        if not self.microphoneAvailable:
            messagebox.showerror(
                "Microphone Not Available",
                "PyAudio is not installed. Microphone features are disabled."
            )
            return
        
        self.listeningMode = "surah"
        self.currentSurah = None
        self.ayahList = []
        self.currentAyahIndex = 0
        self.accumulatedRecitation = ""
        
        self.correctText.config(state=tk.NORMAL)
        self.correctText.delete(1.0, tk.END)
        self.correctText.insert(1.0, "Listening for surah name...\nSay the name of the surah you want to practice (e.g., 'Al-Fatiha', 'الفاتحة', or '1')")
        self.correctText.config(state=tk.DISABLED)
        self.recitedText.delete(1.0, tk.END)
        
        self.feedbackLabel.config(
            text="🎤 Listening for surah name... Please say the surah name clearly.",
            fg="#3498db"
        )
        
        self.startButton.config(state=tk.DISABLED)
        self.stopButton.config(state=tk.NORMAL)
        self.startListening()
    
    def detectSurahFromSpeech(self, recognizedText):
        recognizedTextLower = recognizedText.lower().strip()
        
        for name, surahNum in self.surahNameMapping.items():
            if name.lower() in recognizedTextLower or recognizedTextLower in name.lower():
                if surahNum in self.quranData:
                    return surahNum
        
        numbers = re.findall(r'\d+', recognizedText)
        if numbers:
            try:
                surahNum = int(numbers[0])
                if 1 <= surahNum <= 114 and surahNum in self.quranData:
                    return surahNum
            except ValueError:
                pass
        
        return None
    
    def startPracticeForSurah(self, surahNum):
        if surahNum not in self.quranData:
            self.feedbackLabel.config(
                text=f"❌ Surah {surahNum} not found in the data. Please try again.",
                fg="#e74c3c"
            )
            self.startButton.config(state=tk.NORMAL)
            self.stopButton.config(state=tk.DISABLED)
            return
        
        self.ayahList = []
        ayahNumbers = sorted(self.quranData[surahNum].keys())
        for ayahNum in ayahNumbers:
            self.ayahList.append((surahNum, ayahNum, self.quranData[surahNum][ayahNum]))
        
        if not self.ayahList:
            self.feedbackLabel.config(
                text=f"❌ No ayahs found for Surah {surahNum}",
                fg="#e74c3c"
            )
            self.startButton.config(state=tk.NORMAL)
            self.stopButton.config(state=tk.DISABLED)
            return
        
        self.currentSurah = surahNum
        self.currentAyahIndex = 0
        self.listeningMode = "ayah"
        self.currentAyahCompleted = False
        
        self.feedbackLabel.config(
            text=f"✅ Surah {surahNum} detected! Starting practice with {len(self.ayahList)} ayahs. Beginning with first ayah...",
            fg="#27ae60"
        )
        
        self.root.after(2000, self.displayCurrentAyah)
    
    def displayCurrentAyah(self):
        if self.currentAyahIndex >= len(self.ayahList):
            self.feedbackLabel.config(
                text=f"🎉 Practice session completed! You've recited all {len(self.ayahList)} ayahs of Surah {self.currentSurah}. Well done!",
                fg="#27ae60"
            )
            self.stopListening()
            self.startButton.config(state=tk.NORMAL)
            self.stopButton.config(state=tk.DISABLED)
            return
        
        surahNum, ayahNum, text = self.ayahList[self.currentAyahIndex]
        
        self.correctText.config(state=tk.NORMAL)
        self.correctText.delete(1.0, tk.END)
        self.correctText.insert(1.0, f"Surah {surahNum}, Ayah {ayahNum}:\n{text}")
        self.correctText.config(state=tk.DISABLED)
        
        self.recitedText.delete(1.0, tk.END)
        self.accumulatedRecitation = ""
        self.currentAyahCompleted = False
        
        progress = f"({self.currentAyahIndex + 1}/{len(self.ayahList)})"
        self.feedbackLabel.config(
            text=f"Recite Surah {surahNum}, Ayah {ayahNum} {progress}. Listening...",
            fg="#3498db"
        )
        
        if not self.isListening:
            self.startListening()
    
    def startListening(self):
        if not self.microphoneAvailable:
            messagebox.showerror(
                "Microphone Not Available",
                "PyAudio is not installed. Please install it to use microphone features."
            )
            return
        
        if self.isListening:
            return
        
        self.isListening = True
        self.recitedText.delete(1.0, tk.END)
        self.accumulatedRecitation = ""
        
        thread = threading.Thread(target=self.listenThread, daemon=True)
        thread.start()
    
    def listenThread(self):
        while self.isListening:
            try:
                with self.microphone as source:
                    if self.listeningMode == "surah":
                        audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=10)
                    else:
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                try:
                    if self.listeningMode == "surah":
                        try:
                            recognizedText = self.recognizer.recognize_google(audio, language="ar-SA")
                        except:
                            recognizedText = self.recognizer.recognize_google(audio, language="en-US")
                        
                        surahNum = self.detectSurahFromSpeech(recognizedText)
                        if surahNum:
                            self.isListening = False
                            self.root.after(0, self.startPracticeForSurah, surahNum)
                            break
                        else:
                            self.root.after(0, lambda: self.feedbackLabel.config(
                                text=f"Could not detect surah from '{recognizedText}'. Please say the surah name again (e.g., 'Al-Fatiha', 'الفاتحة', or '1').",
                                fg="#e74c3c"
                            ))
                    else:
                        recognizedText = self.recognizer.recognize_google(audio, language="ar-SA")
                        
                        if self.accumulatedRecitation:
                            self.accumulatedRecitation += " " + recognizedText
                        else:
                            self.accumulatedRecitation = recognizedText
                        
                        self.root.after(0, self.updateRecitedText, recognizedText)
                        self.root.after(0, self.compareRecitation, self.accumulatedRecitation)
                    
                except sr.UnknownValueError:
                    if self.listeningMode == "surah":
                        self.root.after(0, lambda: self.feedbackLabel.config(
                            text="Could not understand. Please say the surah name clearly.",
                            fg="#e74c3c"
                        ))
                    pass
                except sr.RequestError as e:
                    self.root.after(0, lambda: self.feedbackLabel.config(
                        text=f"Error with speech recognition service: {str(e)}",
                        fg="#e74c3c"
                    ))
                    
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                if self.isListening:
                    self.root.after(0, lambda: self.feedbackLabel.config(
                        text=f"Error: {str(e)}",
                        fg="#e74c3c"
                    ))
                break
    
    def updateRecitedText(self, newText):
        currentText = self.recitedText.get(1.0, tk.END).strip()
        if currentText:
            self.recitedText.insert(tk.END, " " + newText)
        else:
            self.recitedText.insert(1.0, newText)
        self.recitedText.see(tk.END)
        
        self.feedbackLabel.config(
            text="Listening... (Your recitation is being transcribed in real-time)",
            fg="#3498db"
        )
    
    def compareRecitation(self, recitedText):
        if self.currentAyahIndex >= len(self.ayahList):
            return
        
        _, _, correctText = self.ayahList[self.currentAyahIndex]
        
        normalizedCorrect = self.normalizeArabic(correctText)
        normalizedRecited = self.normalizeArabic(recitedText)
        
        similarity = difflib.SequenceMatcher(None, normalizedCorrect, normalizedRecited).ratio()
        similarityPercent = similarity * 100
        
        if len(normalizedRecited.strip()) < 3:
            return
        
        if similarityPercent < 80:
            if not hasattr(self, '_lastBuzzTime') or (time.time() - self._lastBuzzTime) > 2:
                self.playBuzzSound()
                self._lastBuzzTime = time.time()
            
            self.highlightIncorrectInTranscript(recitedText, correctText)
            self.highlightCorrectText()
            
            self.feedbackLabel.config(
                text=f"⚠️ Similarity: {similarityPercent:.1f}% - Please correct your recitation. The correct text is highlighted above.",
                fg="#e74c3c"
            )
        else:
            self.highlightCorrectInTranscript()
            
            if not self.currentAyahCompleted:
                self.currentAyahCompleted = True
                self.feedbackLabel.config(
                    text=f"✅ Excellent! Similarity: {similarityPercent:.1f}% - Ayah completed! Moving to next ayah...",
                    fg="#27ae60"
                )
                self.root.after(2000, self.moveToNextAyah)
            else:
                self.feedbackLabel.config(
                    text=f"✅ Excellent! Similarity: {similarityPercent:.1f}% - Your recitation is correct!",
                    fg="#27ae60"
                )
    
    def moveToNextAyah(self):
        if self.currentAyahCompleted:
            self.currentAyahIndex += 1
            self.displayCurrentAyah()
    
    def normalizeArabic(self, text):
        normalized = unicodedata.normalize('NFKD', text)
        normalized = ''.join([c for c in normalized if not unicodedata.combining(c)])
        normalized = ' '.join(normalized.split())
        return normalized.lower()
    
    def highlightCorrectText(self):
        self.correctText.config(state=tk.NORMAL)
        self.correctText.tag_add("highlight", "1.0", tk.END)
        self.correctText.tag_config("highlight", background="#ffeb3b")
        self.correctText.config(state=tk.DISABLED)
        self.root.after(2000, self.removeHighlight)
    
    def removeHighlight(self):
        self.correctText.config(state=tk.NORMAL)
        self.correctText.tag_remove("highlight", "1.0", tk.END)
        self.correctText.config(state=tk.DISABLED)
    
    def highlightIncorrectInTranscript(self, recitedText, correctText):
        self.recitedText.tag_remove("incorrect", "1.0", tk.END)
        self.recitedText.tag_remove("correct", "1.0", tk.END)
        self.recitedText.tag_add("incorrect", "1.0", tk.END)
        self.recitedText.tag_config("incorrect", background="#ffcccc", foreground="#cc0000")
    
    def highlightCorrectInTranscript(self):
        self.recitedText.tag_remove("incorrect", "1.0", tk.END)
        self.recitedText.tag_remove("correct", "1.0", tk.END)
        self.recitedText.tag_add("correct", "1.0", tk.END)
        self.recitedText.tag_config("correct", background="#ccffcc", foreground="#006600")
    
    def playBuzzSound(self):
        try:
            try:
                import numpy as np
                sampleRate = 44100
                duration = 0.3
                frequency = 440
                t = np.linspace(0, duration, int(sampleRate * duration), False)
                wave = np.sin(2 * np.pi * frequency * t)
                wave = wave + 0.3 * np.random.randn(len(wave))
                wave = (wave * 32767).astype(np.int16)
                sound = pygame.sndarray.make_sound(wave)
                sound.play()
            except ImportError:
                self.playSystemBeep()
        except Exception as e:
            try:
                self.playSystemBeep()
            except:
                print(f"Could not play buzz sound: {str(e)}")
    
    def playSystemBeep(self):
        if sys.platform == "darwin":
            os.system("afplay /System/Library/Sounds/Basso.aiff")
        elif sys.platform == "linux":
            os.system("aplay /usr/share/sounds/alsa/Front_Left.wav 2>/dev/null || beep")
        elif sys.platform == "win32":
            import winsound
            winsound.Beep(440, 300)
    
    def stopListening(self):
        self.isListening = False
        self.startButton.config(state=tk.NORMAL)
        self.stopButton.config(state=tk.DISABLED)
        self.feedbackLabel.config(
            text="Listening stopped. Click 'Start Listening for Surah' to begin again.",
            fg="#7f8c8d"
        )


def main():
    root = tk.Tk()
    app = QuranMemorizationTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
