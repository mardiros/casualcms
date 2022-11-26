import React from "react";
import { Box, Button, Heading, Stack } from "@chakra-ui/react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../login/hooks";
import { ApiError } from "../../../casualcms/domain/ports";
import { AppContext } from "../../../config";
import { Setting, SettingType } from "../../../casualcms/domain/model";
import { Loader } from "../../components/loader";
import { ApiErrorUI } from "../../components/error_api";
import { SettingBreadcrumb } from "../../components/breadcrumb";
import { SettingDeletePopoverForm } from "./settings_delete";
// import { SettingBreadcrumb } from "../../components/breadcrumb";
import { Form } from "../../components/jsonschema_form";
import { DownloadIcon } from "@chakra-ui/icons";

export const SettingEdit: React.FunctionComponent<{}> = () => {
  let auth = useAuth();
  const config = React.useContext(AppContext);
  const token = auth.authenticatedUser?.token || "";
  const [setting, setSetting] = React.useState<Setting | null>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const params = useParams();
  const settingKey = params.settingKey || "";
  const hostname = params.hostname || "";

  const [settingType, setSettingType] = React.useState<SettingType | null>(
    null
  );
  const [error, setError] = React.useState<ApiError>(null);
  let navigate = useNavigate();

  React.useEffect(() => {
    async function loadSettingType() {
      const rtyp = await config.api.settingType.showSettingType(
        token,
        settingKey
      );
      rtyp
        .map((typ: SettingType) => setSettingType(typ))
        .mapErr((err: ApiError) => setError(err));
    }
    if (token) {
      loadSettingType();
    }
    return () => {
      setIsLoading(true);
      setError(null);
      setSettingType(null);
    };
  }, [auth, settingKey]);

  React.useEffect(() => {
    async function loadSetting() {
      const rsetting = await config.api.setting.showSetting(
        token,
        hostname,
        settingKey
      );
      rsetting
        .map((setting: Setting) => setSetting(setting))
        .mapErr((err: ApiError) => setError(err));
    }
    if (token) {
      loadSetting();
    }
    return () => {
      setSetting(null);
      setError(null);
    };
  }, [auth, hostname, settingKey]);

  React.useEffect(() => {
    if (settingType && setting) {
      setIsLoading(false);
    }
  }, [settingType, setting, error]);

  if (isLoading) {
    return <Loader label="Loading form..." />;
  }

  const onsubmit = async (data: any) => {
    const setting = data.formData;
    await config.api.setting.updateSetting(token, setting);
    navigate(`/admin/settings/${hostname}`, { replace: true });
  };

  return (
    <Box minW="720px">
      <SettingBreadcrumb hostname={hostname} title={settingKey} />
      <Heading>Edit Setting</Heading>
      {/* <SettingBreadcrumb setting={setting} /> */}
      <ApiErrorUI error={error} />
      {setting && settingType && (
        <>
          <Box maxW="720px">
            <Form
              id="edit-setting"
              schema={settingType.schema}
              uiSchema={settingType.uiSchema}
              formData={setting}
              // onChange={() => console.log("changed")}
              onSubmit={onsubmit}
              // onError={() => console.log("errors")}
            />
          </Box>
          <Stack paddingTop={5} direction="row" align="right">
            <Button
              form="edit-setting"
              type="submit"
              colorScheme="cyan"
              leftIcon={<DownloadIcon />}
            >
              Save
            </Button>
            <SettingDeletePopoverForm curSetting={setting} />
          </Stack>
        </>
      )}
    </Box>
  );
};
