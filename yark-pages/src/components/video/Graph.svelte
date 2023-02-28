<script lang="ts">
	import { VisXYContainer, VisStackedBar, VisAxis } from '@unovis/svelte';
	import { elementWasUpdated, type Element } from '$lib/element';
	import { capitalizeFirstLetter, compactDate } from '$lib/utils';
	import { colors } from '@unovis/ts';

	export let name: string;
	export let trackedElement: Element;
	export let colour: number = 0;

	// Date tick formatting, containing an array of human times corresponding to ticks generated
	let dateTicks: string[] = [];

	/**
	 * Record of a single graph point with x being ticks from 0 to x, and y being the value
	 */
	type GraphRecord = {
		x: number;
		y: any;
	};

	/**
	 * Returns the ideal number of bars the graph should have given infinite data, based on window size
	 */
	function idealBars(): number {
		return Math.max(21, Math.round((window.innerWidth - 150) / 31));
	}

	/**
	 * Scales amount of entries by current window width, allowing for suitable cutoffs
	 * @param entries Entries to scale
	 */
	function xDomainMin(dateTicks: string[]): number {
		return Math.max(0, dateTicks.length - idealBars());
	}

		/**
	 * Calculates how many ticks there will be once {@link xDomainMin} is calculated
	 * @param dateTicks
	 */
	 function ticksInXDomain(dateTicks: string[]): number {
		return Math.min(dateTicks.length, idealBars());
	}

	/**
	 * Converts an element to an array of graph records
	 * @param element Element to convert
	 */
	function elementToGraphRecord(element: Element): GraphRecord[] {
		let records: GraphRecord[] = [];
		const entries = Object.entries(element);
		for (let index = 0; index < entries.length; index++) {
			const [isoString, value] = entries[index];
			dateTicks.push(compactDate(new Date(isoString)));
			records.push({ x: index, y: value });
		}
		return records;
	}

	/**
	 * Gets colour depending on provided index in primary colour array
	 * @param colour Colour index to get (0 to n), based off of graph library
	 */
	function getColour(colour: number): string {
		return colors[colour];
	}

	// Conversion of graph record to ticks
	const x = (d: GraphRecord) => d.x;
	const y = (d: GraphRecord) => d.y;

	// Tick formatting (x-axis labels)
	const tickFormat = (tick: number) => dateTicks[tick];

	$: graphData = elementToGraphRecord(trackedElement);
</script>

<!-- TODO: refresh domain stuff on window change -->
{#if elementWasUpdated(trackedElement)}
	<h2 class="video">{capitalizeFirstLetter(name)} over time</h2>
	<div class="graph">
		<VisXYContainer data={graphData} xDomain={[xDomainMin(dateTicks), dateTicks.length - 1]} >
			<VisStackedBar {x} {y} color={getColour(colour)} roundedCorners={5}/>
			<VisAxis
				type="x"
				{tickFormat}
				numTicks={ticksInXDomain(dateTicks)}
				tickTextFontSize="8.5px"
				tickTextWidth={10}
				
			/>
			<VisAxis type="y" />
		</VisXYContainer>
	</div>
{/if}

<style lang="scss">
	$large: 1300px;

	.graph {
		margin-top: 0.5rem;
		width: calc(100% - 5vw);
		min-width: 40rem;
	}
</style>
