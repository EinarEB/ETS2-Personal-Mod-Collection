# VR Rain Streaks Subtle 0.10.1

A small material adjustment intended to make falling rain streaks less distracting in VR. It sets the diffuse RGB of `material/environment/rain.mat` to `(0.10, 0.10, 0.10)` and references the existing `rain.tobj` texture.

It does not change rain probability, weather selection, windshield droplets, wiper behavior, or traffic. The value 0.10 is a material value; it is not a measured promise of 10% perceived brightness in every lighting setup.

Load above other mods replacing that rain material. Lighting/weather packages may affect the resulting appearance. This release repairs packaging and manifest metadata while retaining the material values. No new VR visual test was performed.
