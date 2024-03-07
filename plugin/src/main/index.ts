import EventEmitter from '../shared/EventEmitter';

figma.showUI(__html__, {
  width: 240,
  height: 256,
  themeColors: true,
});

const getElements = () =>
  figma.currentPage.children.map((node) => ({
    id: node.id,
    name: node.name.substring(0, 20),
  }));

const getFrame = async ({ id, scaling }) => {
  try {
    const node = await figma.getNodeByIdAsync(id);

    if (node && node.type !== 'PAGE' && node.type !== 'DOCUMENT') {
      return {
        id: node.id,
        name: node.name,
        width: node.width,
        height: node.height,
        data: await node.exportAsync({
          format: 'PNG',
          constraint: {
            type: 'SCALE',
            value: scaling || 1,
          },
        }),
      };
    }
  } catch {}

  return null;
};

const sendData = () =>
  EventEmitter.emit('data', {
    elements: getElements(),
    page_name: figma.currentPage.name,
  });

EventEmitter.answer('frame', async (data) => {
  return getFrame(data);
});

EventEmitter.on('get elements', () => {
  figma.notify('Send elements to Blender 🛫');

  sendData();
});

EventEmitter.on('get data', () => {
  figma.notify('Connected with Blender');

  sendData();
});

// events
figma.on('currentpagechange', () => {
  figma.notify('Page changed - send elements to Blender 🛫');

  sendData();
});
