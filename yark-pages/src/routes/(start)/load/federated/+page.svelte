<script lang="ts">
	import { createArchive, setCurrentArchive } from '$lib/archive';
	import { StartCardState } from '$lib/components';
	import Name from '../../../../components/entries/Name.svelte';
	import StartCard from '../../../../components/start/StartCard.svelte';

	let server: string;
	let name: string;

	let serverCompletelyInvalid = false;
	let nameCompletelyInvalid = false;

	/**
	 * Returns validity of the server prop and sets its invalid state it if is
	 */
	function checkServerValidity(): boolean {
		// TODO: merge validation
		serverCompletelyInvalid = server == undefined || server == '';
		return !serverCompletelyInvalid;
	}

	/**
	 * Checks that the name prop is valid
	 */
	function checkNameValidity(): boolean {
		// TODO: merge validation
		nameCompletelyInvalid = name == undefined || name == '';
		return !nameCompletelyInvalid;
	}

	/**
	 * Validates all relevant props
	 * @returns If the inputs are valid or not
	 */
	function validate(): boolean {
		// Check validity beforehand so or doesn't cancel it out
		const serverValid = checkServerValidity();
		const nameValid = checkNameValidity();

		// Return if they're all valid
		return serverValid && nameValid;
	}

	/**
	 * Connects to the archive defined by props, validating them first
	 */
	async function connectArchive() {
		// Validate the inputs
		if (!validate()) {
			return;
		}

		// Skip if anything is missing
		// NOTE: only for getting rid of incorrect typing errors, can delete
		if (server == undefined || name == undefined) {
			return;
		}

		// Connect to remote archive
		const remoteArchive = createArchive(server, name);
		setCurrentArchive(remoteArchive);
	}
</script>

<div class="centre-h">
	<StartCard
		title="Connect"
		description="Connect to a remote federated archive server"
		ballKind={2}
		state={StartCardState.Max}
	>
		<h2 class="card-heading">Direct</h2>
		<input
			type="text"
			placeholder="Server Address"
			bind:value={server}
			on:keydown={() => (serverCompletelyInvalid = false)}
			on:focusout={checkServerValidity}
			class:invalid={serverCompletelyInvalid}
		/>
		<Name bind:name bind:nameCompletelyInvalid />
		<button class="bright" on:click={async () => connectArchive()}>Connect</button>
		<h2 class="card-heading">Discover</h2>
		<div class="coming-soon" />
	</StartCard>
</div>

<style lang="scss">
	.coming-soon {
		width: 175px;
		height: 52.5px;
		background-image: url(/img/comingsoon.png);
		background-size: cover;
		background-repeat: no-repeat;
		border-radius: 7.5px;
		margin-top: 0.25rem;
		margin-bottom: 1.5rem;
		border: 1px solid rgba($color: #000000, $alpha: 0.12);
	}
</style>
