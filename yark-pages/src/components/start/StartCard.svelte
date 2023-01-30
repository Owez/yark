<script lang="ts">
	import Card from '../Card.svelte';
	import StartCardHeader from './StartCardHeader.svelte';

	export let title: string = 'Start Card';
	export let description: string =
		'This is an example of a start card which is part of the Yark design';
	export let link: string = '/';
	export let ballKind: number;
	export let width: string = '18rem';
	export let height: string = '70vh';
</script>

<Card {width} {height} scroll={true}>
	<a href={link} class="invis">
		<div>
			<StartCardHeader {title} {description} {ballKind} />
		</div>
	</a>
	<slot />
</Card>
