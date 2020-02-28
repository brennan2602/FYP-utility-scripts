import numpy as np
import pretty_midi
import glob

#converts a midi file to an array (piano roll representation)
def get_piano_roll(midifile):
    midi_pretty_format = pretty_midi.PrettyMIDI(midifile)
    piano_midi = midi_pretty_format.instruments[0] # Get the piano channels
    piano_roll = piano_midi.get_piano_roll(fs=20)
    print(piano_roll.shape)
    #code to remove silences below
    ind=0
    toRemove=[]
    piano_roll=piano_roll.T
    for column in piano_roll:
        if np.sum(column)==0:
            toRemove.append(ind)
        ind+=1
    print(len(toRemove))
    piano_roll = np.delete(piano_roll,toRemove,0)
    piano_roll = piano_roll.T
    print(piano_roll.shape)
    return piano_roll

#taken from prettyMidi docs
def piano_roll_to_pretty_midi(piano_roll, fs=1, program=0):
    '''Convert a Piano Roll array into a PrettyMidi object
     with a single instrument.
    Parameters
    ----------
    piano_roll : np.ndarray, shape=(128,frames), dtype=int
        Piano roll of one instrument
    fs : int
        Sampling frequency of the columns, i.e. each column is spaced apart
        by ``1./fs`` seconds.
    program : int
        The program number of the instrument.
    Returns
    -------
    midi_object : pretty_midi.PrettyMIDI
        A pretty_midi.PrettyMIDI class instance describing
        the piano roll.
    '''
    notes, frames = piano_roll.shape
    pm = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=program)

    # pad 1 column of zeros so we can acknowledge inital and ending events
    piano_roll = np.pad(piano_roll, [(0, 0), (1, 1)], 'constant')

    # use changes in velocities to find note on / note off events
    velocity_changes = np.nonzero(np.diff(piano_roll).T)

    # keep track on velocities and note on times
    prev_velocities = np.zeros(notes, dtype=int)
    note_on_time = np.zeros(notes)

    for time, note in zip(*velocity_changes):
        # use time + 1 because of padding above
        velocity = piano_roll[note, time + 1]
        time = time / fs
        if velocity > 0:
            if prev_velocities[note] == 0:
                note_on_time[note] = time
                prev_velocities[note] = velocity
        else:
            pm_note = pretty_midi.Note(
                velocity=prev_velocities[note],
                pitch=note,
                start=note_on_time[note],
                end=time)
            instrument.notes.append(pm_note)
            prev_velocities[note] = 0
    pm.instruments.append(instrument)
    return pm



path=r"C:\Users\brenn\Desktop\test"
files=glob.glob(path+"\*.midi") # reading in from folder and getting all .mid
print(files)


#this loop encodes a midi file into a string without ever writing the "#" which is used for silence
#it then decodes a the string back into a midi file
for f in files:
    outString=""
    x= f.split("\\")[-1]
    name=x.split(".midi")[0] #getting name for file
    pr = get_piano_roll(f) #getting piano roll for file with silences removed
    fs = 20
    pm = piano_roll_to_pretty_midi(pr, fs=fs, program=2)  # creating midi file from piano roll array
    pm.write(path+"\\"+name+"NoSilence.midi")






