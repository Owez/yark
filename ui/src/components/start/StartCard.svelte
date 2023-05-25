<script lang="ts">
    export let title = "Example";
    export let description =
        "Lorem ipsum here like create an archive from scratch";
    export let ball = 0;
    export let big = false;

    function getBall(): string {
        return `/img/ball${ball + 1}.png`;
    }
</script>

<div class="card">
    <img src={getBall()} alt={title} class="ball" />
    <h1>{title}</h1>
    <p>{description}</p>
    <slot />
</div>

<style lang="scss">
    .card {
        width: calc(15rem + 10vw);
        height: calc(40vh + 10rem);
        border: 1px solid rgba($color: #000000, $alpha: 0.12);
        border-radius: 7.5px;
        box-sizing: border-box;
        padding: 30px;
    }

    .ball {
        $size: 60px;
        width: $size;
        height: $size;
        margin-bottom: 25px;
    }

    h1 {
        font-weight: 500;
        font-size: 1.5rem;
    }

    p {
        $margin: 20px;
        margin-top: $margin;
        margin-bottom: $margin;
        line-height: 1.5;
    }
</style>
