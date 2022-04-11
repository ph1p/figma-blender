import EventEmitter from '../shared/EventEmitter';

figma.showUI(__html__, {
  width: 240,
  height: 216,
});

const getElements = () =>
  figma.currentPage.children.map((node) => ({
    id: node.id,
    name: node.name,
  }));

const getFrame = async (id) => {
  try {
    const node = figma.getNodeById(id);

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
            value: 1,
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

EventEmitter.answer('frame', async (id) => {
  return getFrame(id);
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
