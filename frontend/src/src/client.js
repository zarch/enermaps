import {BASE_URL} from './settings.js';

export const WMS_URL = BASE_URL + 'api/wms?';

export async function getCMs() {
  const response = await fetch(BASE_URL + 'api/cm/');
  if (!response.ok) {
    return [];
  }
  const cmsResponse = await response.json();
  return cmsResponse.cms;
}

// Get one geofile
export async function getGeofile(layer_id) {
    const response = await fetch(BASE_URL + 'api/geofile/' + layer_id);
    if (!response.ok) {
      console.log(response);
      //TODO return something else than a list
      return [];
    }
    const layerResponse = await response.json();
    return layerResponse;
}

// Get all stored geofiles
export async function getGeofiles() {
  const response = await fetch(BASE_URL + 'api/geofile');
  if (!response.ok) {
    console.log(response);
    return [];
  }
  const layersResponse = await response.json();
  return layersResponse;
}


export async function postCMTask(cm, parameters) {
  const response = await fetch(BASE_URL + 'api/cm/' + cm.name + '/task', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(parameters),
  });
  const task = await response.json();
  return {'cm': cm, 'id': task.task_id};
}

export async function getTaskResult(cm, task) {
  const taskResponse = await fetch(BASE_URL + 'api/cm/' + cm.name + '/task/' + task.id);
  return await taskResponse.json();
}

export async function deleteTaskResult(cm, task) {
  const taskResponse = await fetch(BASE_URL + 'api/cm/' + cm + '/task/' + task.id, {
    method: 'DELETE',
  });
  return await taskResponse.json();
}
