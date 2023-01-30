<script lang="ts">
	import { StartCardState } from '$lib/components';
	import Card from '../Card.svelte';
	import StartCardHeader from './StartCardHeader.svelte';

	export let title: string = 'Start Card';
	export let description: string =
		'This is an example of a start card which is part of the Yark design';
	export let href: string = '/';
	export let ballKind: number;
	export let state: StartCardState = StartCardState.Full;
	export let margin: string | undefined = undefined;
</script>

<Card startCard={state} {margin}>
	<a {href} class="invis">
		<div>
			<StartCardHeader {title} {description} {ballKind} />
		</div>
	</a>
	<slot />
</Card>
