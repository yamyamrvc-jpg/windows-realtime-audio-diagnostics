# Virtual Audio Cable Checklist

This checklist is generic guidance for VB-CABLE-style virtual microphone routing on Windows.

## Basic Routing

- Select the virtual cable playback endpoint in the sending application.
- Select the matching virtual cable recording endpoint in the receiving application.
- Confirm Windows did not switch either app back to the system default device.
- Test with a known audio source before testing your realtime application.

## Windows Sound Settings

- Open Windows Sound settings and inspect input and output devices.
- Check the advanced properties for sample rate and channel count.
- Use the same sample rate across the sending app, receiving app, and virtual cable when possible.
- Disable audio enhancements while troubleshooting.
- Check whether exclusive mode is enabled and whether another app may be holding the endpoint.

## App Settings

- Write down the exact input and output device names selected in each app.
- Confirm the app is using the expected host API if it exposes one.
- Keep buffer size and sample rate choices consistent while comparing logs.
- Restart apps after changing device defaults or driver settings.

## Symptoms

- No signal: check that the sender is playing to the cable input and the receiver is listening to the cable output.
- Distortion: lower gain and check for clipping.
- Dropouts: inspect callback jitter, late chunks, and output underflows.
- Delay: reduce prefill or buffer sizes carefully, then watch for underflows.
- Drift: check for sample rate mismatch between endpoints.

## Evidence To Capture

- Screenshot or text notes of Windows device settings.
- App input/output selections.
- Sample rate, channels, and buffer size.
- A short anonymous log excerpt.
- WAV stats for a short test recording if clipping is suspected.
