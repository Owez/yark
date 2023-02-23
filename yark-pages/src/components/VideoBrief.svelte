<script lang="ts">
	import { getVideoThumbnailLink, type ArchiveBriefVideo } from '$lib/archive';

	export let video: ArchiveBriefVideo;
</script>

<a href={`/video/${video.id}`} class="video invis">
	<div class="thumbnail">
		<img src={getVideoThumbnailLink(video)} alt={video.title} class="card-border" />
	</div>
	<div class="info">
		<p class="title">{video.title}</p>
	</div>
</a>

<style lang="scss">
	$width: 225px;

	.video {
		display: flex;
		flex-direction: column;
		margin-right: 1rem;
		margin-bottom: 1rem;
	}

	.thumbnail {
		width: $width;
		height: 126.5625px;

		img {
			width: 100%;
			height: 100%;
		}
	}

	.info {
		display: flex;
		justify-content: space-between;
		width: $width;
		margin-top: 0.5rem;
	}

	.title {
		max-width: $width - 35px;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		font-size: small;
	}
</style>
