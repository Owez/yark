<script lang="ts">
	import { getVideoFileApiLink, videoWasUpdated, type VideoDetailed } from '$lib/archive';
	import { getCurrentElement } from '$lib/element';
	import { humanDateFromIso } from '$lib/utils';

	export let video_id: string;
	export let video: VideoDetailed;

	$: views = getCurrentElement(video.views);
	$: uploaded = humanDateFromIso(video.uploaded);
	$: file_link = getVideoFileApiLink(video_id);
</script>

<div class="info">
	<p>
		<span>{views} views</span>
		<span class="spacer">•</span>
		<span>{uploaded}</span>
		{#if videoWasUpdated(video)}
			<span class="spacer">•</span>
			<span>🌀</span>
		{/if}
	</p>
	<p>
		<a
			href={`https://www.youtube.com/watch?v=${video_id}`}
			target="_blank"
			rel="noopener noreferrer"
			class="invis">🔗</a
		>
		<span class="spacer">•</span>
		<a href={file_link} target="_blank" rel="noopener noreferrer" download>💾</a>
	</p>
</div>

<style lang="scss">
	$large: 1300px;
	$grey: #7f7f7f;

	.info {
		color: $grey;
		display: flex;
		justify-content: space-between;
		font-size: 0.925rem;
		line-height: 1.25rem;

		.spacer {
			margin-left: 0.35rem;
			margin-right: 0.35rem;
		}
	}

	@media (max-width: $large) {
		.info {
			width: 40rem;
		}
	}

	@media (min-width: $large) {
		.info {
			width: 55rem;
		}
	}
</style>
