<script lang="ts">
	import { Archive } from '$lib/archive';
	import { StartCardState } from '$lib/components';
	import StartCard from '../../../../components/start/StartCard.svelte';

	// NOTE: uncomment if discovery is implemented
	// /**
	//  * Returns if the consent dialog should be shown to the user
	//  * @param store Yark store to check if it's been asked before
	//  */
	// function shouldShowConsent(store: YarkStore): boolean {
	// 	return !store.federatedAccept;
	// }

	let server: string;
	let slug: string;
</script>

<div class="centre-h">
	<StartCard
		title="Connect"
		description="Connect to a remote federated archive server"
		ballKind={2}
		state={StartCardState.Max}
	>
		<h2 class="card-heading">Direct</h2>
		<input type="text" name="direct-url" id="direct-url" placeholder="URL" bind:value={server} />
		<input
			type="text"
			name="direct-name"
			id="direct-name"
			class="mini"
			placeholder="Name"
			bind:value={slug}
		/>
		<button class="bright bottom-element" on:click={() => new Archive(server, slug).setAsCurrent()}
			>Connect</button
		>
		<!-- NOTE: uncomment if discovery is implemented -->
		<!-- {#if shouldShowConsent($yarkStore)}
		{:else}
		{/if} -->
	</StartCard>
</div>

<style lang="scss">
	.bottom-element {
		margin-bottom: 1.5rem;
	}
</style>
