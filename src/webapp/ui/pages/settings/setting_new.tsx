import React from "react";
import { Box, Button, Heading, Icon, Stack } from "@chakra-ui/react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../login/hooks";
import { ApiError } from "../../../casualcms/domain/ports";
import { AppContext } from "../../../config";
import { SettingType } from "../../../casualcms/domain/model";
import { Loader } from "../../components/loader";
import { ApiErrorUI } from "../../components/error_api";
import { SettingBreadcrumb } from "../../components/breadcrumb";
import { Form } from "../../components/jsonschema_form";
import { DownloadIcon } from "@chakra-ui/icons";

export const SettingNew: React.FunctionComponent<{}> = () => {
  let { hostname, settingKey } = useParams<string>();
  let auth = useAuth();
  const config = React.useContext(AppContext);
  const token = auth.authenticatedUser?.token || "";
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [settingType, setSettingType] = React.useState<SettingType | null>(
    null
  );
  const [error, setError] = React.useState<ApiError>(null);
  let navigate = useNavigate();

  React.useEffect(() => {
    async function loadType() {
      const rtyp = await config.api.settingType.showSettingType(
        token,
        settingKey || ""
      );
      rtyp
        .map((typ: SettingType) => setSettingType(typ))
        .mapErr((err: ApiError) => setError(err));
      setIsLoading(false);
    }
    if (token) {
      loadType();
    }
    return () => {
      setIsLoading(true);
      setError(null);
      setSettingType(null);
    };
  }, [auth, hostname, settingKey]);

  if (isLoading) {
    return <Loader label="Loading form..." />;
  }
  const onsubmit = async (data: any) => {
    const setting = data.formData;
    await config.api.setting.createSetting(
      token,
      hostname || "",
      settingKey || "",
      setting
    );
    navigate(`/admin/settings/${hostname}`, { replace: true });
  };

  const data = {};
  return (
    <Box minW="720px">
      <SettingBreadcrumb hostname={hostname} title={settingKey} />
      <Heading>New Setting</Heading>
      {/* <SettingBreadcrumb title="new setting" /> */}
      <ApiErrorUI error={error} />
      {settingType && (
        <>
          <Box maxW="720px">
            <Form
              id="new-setting"
              schema={settingType.schema}
              uiSchema={settingType.uiSchema}
              formData={data}
              // onChange={() => console.log("changed")}
              onSubmit={onsubmit}
            // onError={() => console.log("errors")}
            />
          </Box>
          <Stack paddingTop={5} direction="row" align="right">
            <Button form="new-setting" type="submit" colorScheme="cyan">
              <Icon as={DownloadIcon} marginEnd={2} />
              Create Setting
            </Button>
          </Stack>
        </>
      )}
    </Box>
  );
};
