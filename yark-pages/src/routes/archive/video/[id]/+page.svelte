<script lang="ts">
	import { getVideoFileApiLink, videoWasUpdated } from '$lib/archive';
	import { elementUpdateCount, getCurrentElement } from '$lib/element';
	import { humanDateFromIso } from '$lib/utils';
	import HistoryItem from '../../../../components/HistoryItem.svelte';
	import type { PageData } from './$types';

	export let data: PageData;

	let descriptionShowing = false;

	$: titleEntries = Object.entries(data.video.title);
	$: descriptionEntries = Object.entries(data.video.description);
</script>

<p class="back-button">
	<a href="/archive/videos" class="invis">
		<img src="/img/btnback.svg" alt="Back" />
		<span class="text">Back</span>
	</a>
</p>
<!-- NOTE: workaround for <https://github.com/sveltejs/svelte/issues/5967> -->
<!-- svelte-ignore a11y-media-has-caption -->
<video controls autoplay>
	<source src={getVideoFileApiLink(data.id)} type="video/mp4" />
</video>
<h1>{getCurrentElement(data.video.title)}</h1>
<div class="info">
	<p>
		<span>{getCurrentElement(data.video.views)} views</span>
		<span class="spacer">•</span>
		<span>{humanDateFromIso(data.video.uploaded)}</span>
		{#if videoWasUpdated(data.video)}
			<span class="spacer">•</span>
			<span>🌀</span>
		{/if}
	</p>
	<p>
		<a
			href={`https://www.youtube.com/watch?v=${data.id}`}
			target="_blank"
			rel="noopener noreferrer"
			class="invis">🔗</a
		>
		<span class="spacer">•</span>
		<a href={getVideoFileApiLink(data.id)} target="_blank" rel="noopener noreferrer" download>💾</a>
	</p>
</div>
{#if getCurrentElement(data.video.description) != undefined}
	<button
		class="bright description-button"
		on:click={() => (descriptionShowing = !descriptionShowing)}
	>
		{#if descriptionShowing}
			Hide
		{:else}
			Show
		{/if}
		Description
	</button>
	{#if descriptionShowing}
		<p class="description">
			{#each getCurrentElement(data.video.description).split('\n') as line}
				{line}<br />
			{/each}
		</p>
	{/if}
{/if}
<h2>History</h2>
<ul>
	{#if titleEntries.length < 2}
		<li>No title changes on record</li>
	{:else}
		{#each titleEntries as entry, ind}
			<HistoryItem name="title" {entry} {ind} />
		{/each}
	{/if}
	{#if descriptionEntries.length < 2}
		<li>No description changes on record</li>
	{:else}
		{#each descriptionEntries as entry, ind}
			<HistoryItem name="description" {entry} {ind} />
		{/each}
	{/if}
</ul>

<style lang="scss">
	$medium: 765px;
	$large: 1300px;
	$grey: #7f7f7f;

	.back-button {
		$margin-v: 3.35rem;
		$padding-v: 1rem;

		margin: 0;
		margin-top: $margin-v - $padding-v;
		padding-bottom: $padding-v * 0.5;

		.text {
			font-size: smaller;
			margin-left: 0.3rem;
			font-weight: 500;
			color: #666766;
			padding-top: $padding-v;
			padding-right: 3rem;
		}
	}

	video {
		background-color: black;
		border-radius: 7.5px;
		aspect-ratio: 16/9;
	}

	h1,
	h2 {
		font-weight: 450;
	}

	h1 {
		font-size: x-large;
		margin-top: 0.75rem;
	}

	h2 {
		font-size: large;
		margin-top: 1rem;
		margin-bottom: 0.25rem;
	}

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

	.description-button {
		margin-top: 1rem;
	}

	.description {
		color: $grey;
		margin-left: 1rem;
		margin-top: 0.25rem;
		font-size: smaller;
		line-height: 1.25rem;
	}

	@media (max-width: $medium) {
		video,
		.info {
			width: 25rem;
		}
	}

	@media (min-width: $medium) and (max-width: $large) {
		video,
		.info,
		.description {
			width: 40rem;
		}
	}

	@media (min-width: $large) {
		video,
		.info,
		.description {
			width: 55rem;
		}
	}
</style>
