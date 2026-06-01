# Realtime Audio Glossary

## Callback Jitter

Callback jitter is variation in the time between audio callbacks. Low-latency systems expect callbacks to arrive at regular intervals. Large jitter can cause a callback to run too late even when average processing time looks acceptable.

## Underflow

An output underflow happens when the playback side needs audio samples but the application has not provided them in time. Users may hear dropouts, gaps, clicks, or brief silence.

## Overflow

An input overflow happens when captured audio arrives faster than the application consumes it. Some input samples may be dropped before the application can process them.

## Buffer Prefill

Buffer prefill is the amount of audio queued before playback starts or resumes. More prefill can reduce underflows, but it usually increases latency.

## Sample Rate Mismatch

A sample rate mismatch occurs when devices, files, or application stages disagree about rates such as 44.1 kHz and 48 kHz. Mismatches can cause resampling, timing drift, pitch changes in broken pipelines, or avoidable latency.

## Clipping

Clipping occurs when sample values exceed the representable range and are limited to the maximum or minimum value. It can sound harsh and may indicate too much gain somewhere in the chain.

## dBFS

dBFS means decibels relative to full scale. In digital audio, 0 dBFS is the maximum representable level. Normal unclipped signals usually peak below 0 dBFS.

## Virtual Audio Routing

Virtual audio routing uses software devices to send audio from one application into another. On Windows, virtual cable tools often expose one endpoint that acts like a speaker/playback device and another endpoint that acts like a microphone/capture device.
