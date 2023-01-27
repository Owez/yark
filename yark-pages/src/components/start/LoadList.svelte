<script lang="ts">
	import { yarkStore } from '$lib/store';
	import type { Archive } from '$lib/yark';

	export let count: number = 4;

	/**
	 * Gets most recent archives up to the count
	 */
	function getArchives(): Archive[] {
		return $yarkStore.recents.reverse().slice(0, count);
	}
</script>

<div class="list">
	{#each getArchives() as archive}
		<a href={archive.getUrl()} class="item invis">
			<p class="name">{archive.getName()}</p>
		</a>
	{/each}
</div>

<style lang="scss">
	.list {
		margin-top: 1.25rem;
		margin-bottom: 1.25rem;
	}

	.item {
		$margin-v: 0.5rem;
		$padding-h: 0.75rem;

		background: rgb(255, 255, 255);
		background: linear-gradient(142deg, rgb(247, 247, 247) 0%, rgba(244, 244, 244, 1) 100%);
		height: 2rem;
		display: flex;
		align-items: center;
		margin-top: $margin-v;
		margin-bottom: $margin-v;
		padding-left: $padding-h;
		padding-right: $padding-h;
		border-radius: 7.5px;
	}

	p {
		margin: 0;
	}
</style>
