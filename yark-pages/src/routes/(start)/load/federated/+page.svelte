<script lang="ts">
	import { StartCardState } from '$lib/components';
	import { yarkStore, type YarkStore } from '$lib/store';
	import StartCard from '../../../../components/start/StartCard.svelte';

	/**
	 * Returns if the consent dialog should be shown to the user
	 * @param store Yark store to check if it's been asked before
	 */
	function shouldShowConsent(store: YarkStore): boolean {
		return !store.federatedAccept;
	}
</script>

<div class="centre-h">
	<StartCard
		title="Connect"
		description="View someone else's federated archive server"
		ballKind={2}
		state={StartCardState.Max}
	>
		<h2 class="card-heading">Direct Connect</h2>
		<input type="text" name="direct-url" id="direct-url" />
		<button>Connect</button>
		<h2 class="card-heading">Discover</h2>
		{#if shouldShowConsent($yarkStore)}
			<!-- TODO: consent -->
		{:else}
			<!-- TODO: discover listing -->
		{/if}
	</StartCard>
</div>
