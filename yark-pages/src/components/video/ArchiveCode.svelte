<script lang="ts">
	import Highlight, { LineNumbers } from 'svelte-highlight';
	import json from 'svelte-highlight/languages/typescript';
	import atomOneLight from 'svelte-highlight/styles/atom-one-light';

	export let videoRawArchive: string;

	const version = '4';
</script>

<svelte:head>
	{@html atomOneLight}
</svelte:head>

<h2 class="video">Archive Code</h2>
<p class="video">Version {version}</p>
<div class="code" title={`Underlying archive code for this video (version ${version})`}>
	<Highlight language={json} code={videoRawArchive} let:highlighted>
		<LineNumbers {highlighted} hideBorder />
	</Highlight>
</div>

<style lang="scss">
	$large: 1300px;

	.code {
		font-size: smaller;
		width: 40rem;
		overflow-x: auto;
		margin-top: 0.5rem;
	}

	@media (max-width: $large) {
		.code {
			width: 40rem;
		}
	}

	@media (min-width: $large) {
		.code {
			width: 55rem;
		}
	}
</style>
