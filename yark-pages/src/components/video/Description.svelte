<script lang="ts">
	import type { VideoDetailed } from '$lib/archive';
	import { getCurrentElement } from '$lib/element';

	export let video: VideoDetailed;

	let showing = false;

	$: description = getCurrentElement(video.description);
</script>

{#if description != undefined}
	<button class="bright description-button" on:click={() => (showing = !showing)}>
		{#if showing}
			Hide
		{:else}
			Show
		{/if}
		Description
	</button>
	{#if showing}
		<p class="description">
			{#each description.split('\n') as line}
				{line}<br />
			{/each}
		</p>
	{/if}
{/if}

<style lang="scss">
	$large: 1300px;
	$grey: #7f7f7f;

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

	@media (max-width: $large) {
		.description {
			width: 40rem;
		}
	}

	@media (min-width: $large) {
		.description {
			width: 55rem;
		}
	}
</style>
