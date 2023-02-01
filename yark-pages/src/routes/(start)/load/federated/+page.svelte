<script lang="ts">
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
</script>

<div class="centre-h">
	<StartCard
		title="Connect"
		description="View someone else's federated archive server"
		ballKind={2}
		state={StartCardState.Max}
	>
		<h2 class="card-heading">Direct Connect</h2>
		<input type="text" name="direct-url" id="direct-url" placeholder="e.g. https://example.com" />
		<button class="bright bottom-element">Connect</button>
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
