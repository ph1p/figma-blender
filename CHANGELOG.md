# 1.0.0 (2026-11-22)


* feat(addon)!: package as Blender extension with bundled websockets ([db2e9d6](https://github.com/ph1p/figma-blender/commit/db2e9d6db3095b59f03918e87ac9ce79f826dab4))


### Bug Fixes

* **addon:** install websockets into a writable directory ([7f1a121](https://github.com/ph1p/figma-blender/commit/7f1a1212a86fe48e0ecf5dc51b62306e1cdf2a3d))
* **addon:** keep the event loop pump alive across file loads ([e0e6d6b](https://github.com/ph1p/figma-blender/commit/e0e6d6bef4f1e664c5fdee20c322f97f541d989d))
* **addon:** keep the live connection when a second one is rejected ([3d29309](https://github.com/ph1p/figma-blender/commit/3d2930905e32f980cdd811447ef0809d897bfa4f))
* **addon:** link the image alpha so transparent areas are not black ([e04c24b](https://github.com/ph1p/figma-blender/commit/e04c24b0dd5deb614215013b8d62869cf484520c))
* **addon:** release port 1410 when the server stops ([d4184a4](https://github.com/ph1p/figma-blender/commit/d4184a4201b0b1a45bfd2a93232351c0981a6ac5))
* **addon:** use the platform temp dir instead of a hardcoded /tmp/ ([8f3a11d](https://github.com/ph1p/figma-blender/commit/8f3a11d504529a06b9386836cff947f8267bacd8))
* check bsdf material ([89856d5](https://github.com/ph1p/figma-blender/commit/89856d50d4b67dfccbccb07fd4c578e7c2588032))
* harden addon and plugin, version the wire protocol ([03d29ea](https://github.com/ph1p/figma-blender/commit/03d29ea39e8b4b024b0e51aa6ad04b2e7cc344f8))
* **panel:** fix a condition ([db0656e](https://github.com/ph1p/figma-blender/commit/db0656e9a0fef4c5f07fd3d01ef5b7502a450c16))
* **server:** handle server error and add items to global object ([cee65ca](https://github.com/ph1p/figma-blender/commit/cee65cadd426e80f34d6563828e61d8da901e8d0))
* **sync:** update props, update panel UI, fix bug with faces ([0ce1c4f](https://github.com/ph1p/figma-blender/commit/0ce1c4f66dfe16c501c597e9c11e1244167e4fdb))


### Features

* **alpha/scale:** update imported image scale and add alpha channel link ([e6da7b1](https://github.com/ph1p/figma-blender/commit/e6da7b171f6e10105e6db7a423bfe38e94c5d7b0)), closes [#1](https://github.com/ph1p/figma-blender/issues/1)
* **dark-mode:** add dark mode and update deps ([aa12f07](https://github.com/ph1p/figma-blender/commit/aa12f07ee9da339e8be1f6e5297af20d1b7563ff))
* **faces:** add ability to change face material ([4e81d14](https://github.com/ph1p/figma-blender/commit/4e81d1464c34ebba33be851678599f0f2fd508c1))
* **path:** handle dir path and add errors ([e71f8e3](https://github.com/ph1p/figma-blender/commit/e71f8e3af8a4c249feab5de2e95be393a29eccaa))
* **plugin:** figma-style UI and scale dropdown ([71fabff](https://github.com/ph1p/figma-blender/commit/71fabffbc835d9e1beb5ba7e7aecfe470db6869a))
* **plugin:** refresh the element list without restarting Blender ([5782738](https://github.com/ph1p/figma-blender/commit/57827380d97a278e1cd74e5014f1eb335e25c0bf))
* **slug:** slugify the element name ([4e9d2c8](https://github.com/ph1p/figma-blender/commit/4e9d2c853e65c5c5ab2e92097cba50d52e95c51e))
* support newest blender version and fix a lot of bugs, also improve websocket server ([7bf1680](https://github.com/ph1p/figma-blender/commit/7bf16809b3d8b0f82ea83db677b1746ea5c94adf))


### BREAKING CHANGES

* the addon id is now figma_connect and needs Blender 4.2+.
Remove the old "Figma" add-on before installing.
