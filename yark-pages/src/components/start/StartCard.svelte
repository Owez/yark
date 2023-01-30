<script lang="ts">
	import Card from '../Card.svelte';
	import StartCardHeader from './StartCardHeader.svelte';

	export let title: string = 'Start Card';
	export let description: string =
		'This is an example of a start card which is part of the Yark design';
	export let href: string = '/';
	export let ballKind: number;
	export let half: boolean = false;
</script>

<Card startCard startCardHalf={half}>
	<a {href} class="invis">
		<div>
			<StartCardHeader {title} {description} {ballKind} />
		</div>
	</a>
	<slot />
</Card>
