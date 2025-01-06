# rpi-epaper-api

A rest API for setting the display image on a [Waveshare 4.26"](https://www.waveshare.com/4.26inch-e-paper-hat.htm) 
eink HAT connected to a Raspberry Pi. Supports scaling and rotating the input image. Endpoints are also provided for
fetching display contents and clearing the display.

This project utilises the [Waveshare e-paper SDKs](https://github.com/waveshareteam/e-Paper) for handling the device commands. This SDK does not seem to have
any official documentation, the API usage was obtained from these pages:
- [Waveshare display manual](https://www.waveshare.com/wiki/4.26inch_e-Paper_HAT_Manual)
- [epd test script](https://github.com/waveshareteam/e-Paper/blob/master/RaspberryPi_JetsonNano/python/examples/epd_4in26_test.py)
- [epd library code](https://github.com/waveshareteam/e-Paper/blob/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd4in26.py)

For convenience, this tool is packaged as a docker container. It can also be run on bare metal, but you will need to
add the Waveshare SDK to your path (see [Dockerfile](./Dockerfile)).

⚠️ The API is served via the Flask development webserver - you should not expose it publicly.

⚠️ A shared instance of the `epd` object is used across requests, therefore it is not possible to run this application
on a webserver with more than a single worker, should you choose to use a webserver other than the Flask development
webserver.

## Setup

### Install on a Raspberry Pi + Display

Build and run the container:

```commandline
git clone https://github.com/adriankeenan/rpi-epaper-api.git
docker build -t rpi-eink-api .
docker run -p 5000:5000 --restart=always --privileged rpi-eink-api
```

Now you're ready to send images to the display!

`--restart=always` will ensure that the container is restarted on crash and on system boot. 

### Running locally

You can run also run the API locally using the `EPD_MOCK=true` env var to mock all calls to the display itself.
You can still check that the correct image is produced by looking at `src/img.png`.

```commandline
EPD_MOCK=true python3 src/server.py
```

## API

### Setting the image

`POST http://rpi:5000`

Set image from file
```commandline
curl --form upload=@image.jpg --form resize=FIT --form background=WHITE http://rpi:5000
```

Set image from pipe
```commandline
cat image.jpg | curl --form image=@- --form resize=FIT --form background=WHITE http://rpi:5000
```

Data should be sent form-encoded.

| Field        | Description                                                                                                                                                                                                                           | Default | Required |
|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|----------|
| `image`      | Image file to display. Any image type supported by the Python PIL library should work.                                                                                                                                                | N/A     | Yes      |
| `mode`       | Display mode, corresponding to the `display_XXX` method on the `epd` object.<br>`FAST` - uses `display_Fast` for a complete screen refresh.<br>`PARTIAL` - uses `display_Partial` for incremental updates (which may cause ghosting). | `FAST`  | No       |
| `dither`     | Whether to enable dithering when converting image to mono chromatic. `true` or `1` to enable.                                                                                                                                         | `true`  | No       |
| `resize`     | `FIT` Resize keeping aspect ratio, without cropping.<br>`CROP` Resize keeping aspect ratio, with cropping.<br>`STRETCH` fill display, ignoring aspect ratio.<br>`NONE` Display without any scaling, pixels drawn 1:1.                 | `FIT`   | No       |
| `rotate`     | Number of degrees to rotate counter-clockwise, supports increments of 90 degrees.                                                                                                                                                     | `0`     | No       |
| `background` | Background colour to use if the image doesn't fill the display. Either `WHITE` or `BLACK`.                                                                                                                                            | `WHITE` | No       |

Expect this call to take ~5 seconds. 

Display update will be skipped if the resulting image is the same as the last request (see `updated` field in the response). 

### Fetching the current image

`GET http://rpi:5000`

```commandline
curl http://rpi:5000 -o img.png
```

Returns the last image (as PNG) that was successfully sent to the display. This is the exact framebuffer sent to the device (eg post-scaling).
This is useful for checking the scaling and rotation settings are correct.

This image is not persisted between restarts of the container.

### Clearing the current image

`DELETE http://rpi:5000`

```commandline
curl -X DELETE http://rpi:5000
```

Expect this call to take ~7 seconds.

Reverts all pixels to the off (white) state. 

## Notes

- Although this is project is intended only for the 4.26" e-paper display, it's likely that other displays can be supported
  by changing the imported EDP object.

# License

[MIT](./LICENSE)