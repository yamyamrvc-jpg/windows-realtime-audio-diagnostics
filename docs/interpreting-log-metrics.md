# Interpreting Log Metrics

Realtime audio logs vary by application, but many contain similar signals.

## Late Chunks

Late chunks mean an audio block missed its expected deadline. A small number during startup may be less important than repeated late chunks during steady-state audio.

Useful next checks:

- Compare `avg_ms` with `max_ms`.
- Look for spikes in `callback_jitter_ms`.
- Check whether late chunks coincide with underflows.

## Underflows

`output_underflows` means playback asked for audio before enough samples were ready. Underflows often match audible gaps or clicks.

Common causes include:

- Processing spikes.
- Too little buffer prefill.
- Device or driver scheduling delays.
- Sample rate mismatch or unexpected resampling.

## Overflows

`input_overflows` means capture data was not consumed quickly enough. This may drop microphone samples before processing.

## Jitter

`callback_jitter_ms` is timing variation around the expected callback interval. High jitter can be more important than average processing time because deadlines are missed at the worst moments.

## Peak, RMS, and Clipping

Peak level shows the largest absolute sample value. RMS estimates average signal energy. In dBFS, values near 0 dBFS are close to digital full scale.

If `clipped_sample_ratio` is greater than zero, some samples reached full scale. A tiny ratio may still be audible depending on content, so inspect the file and gain staging.

## Prefill and Ring Fill

`target_prefill_ms` and `ring_fill_ms` describe how much audio is queued. Higher values can reduce underflows but increase latency. Lower values reduce latency but leave less time to recover from scheduling jitter.

## Cache Flags

Cache flags such as `cache_enabled` are application-specific hints. They are useful when comparing runs, but they do not prove performance by themselves. Compare them with timing metrics and audible results.
